#!/usr/bin/env python3
"""Compare Python implementations on programs from the Shed Skin examples.

Each implementation in config.toml is built from a git ref and cached in the
work directory (or is an installed interpreter); programs are run and timed
one at a time, and results are kept in <work>/results.json, so an
interrupted run picks up where it stopped.

    pybench.py list                               # implementations, built or not
    pybench.py build [IMPL ...]                   # clone and build
    pybench.py run [-i IMPL ...] [-p PROG ...]    # time programs
    pybench.py report                             # table of times/speedups

Needs Python 3.11+, git, a C/C++ toolchain, and for the CPython JIT builds
the LLVM version named in the config. PyPy is translated from source unless
--pypy names an installed PyPy to use instead.
"""

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
JOBS = os.cpu_count() or 1


def slug(name):
    return re.sub(r"[^a-z0-9.]+", "-", name.lower()).strip("-")


def sh(cmd, cwd=None, env=None, log=None):
    """Run a command, appending its output to log; raise on failure."""
    print("+", " ".join(map(str, cmd)), flush=True)
    if log:
        with open(log, "a") as f:
            f.write(f"\n$ {' '.join(map(str, cmd))}\n")
            f.flush()
            res = subprocess.run(cmd, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT)
    else:
        res = subprocess.run(cmd, cwd=cwd, env=env)
    if res.returncode:
        raise RuntimeError(f"command failed ({res.returncode}): {cmd}" + (f", see {log}" if log else ""))


def git_checkout(url, ref, dest):
    """Shallow checkout of a tag, branch or commit; returns the commit."""
    if not (dest / ".git").exists():
        dest.mkdir(parents=True, exist_ok=True)
        sh(["git", "init", "-q"], cwd=dest)
        sh(["git", "remote", "add", "origin", url], cwd=dest)
        sh(["git", "fetch", "-q", "--depth", "1", "origin", ref], cwd=dest)
        sh(["git", "checkout", "-q", "FETCH_HEAD"], cwd=dest)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dest, text=True).strip()


class Bench:
    def __init__(self, config, work):
        self.work = work
        self.cfg = tomllib.loads(config.read_text())
        self.impls = {i["name"]: i for i in self.cfg["impl"]}
        self.results_path = work / "results.json"
        self.results = json.loads(self.results_path.read_text()) if self.results_path.exists() else {}

    def save(self):
        tmp = self.results_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.results, indent=1, sort_keys=True))
        tmp.replace(self.results_path)

    # --- building implementations

    def build_impl(self, impl):
        """Ensure impl (or the build it uses) is built; returns its stamp."""
        impl = self.impls[impl.get("uses", impl["name"])]
        if "exe" in impl:
            exe = shutil.which(impl["exe"])
            if not exe:
                raise SystemExit(f"{impl['name']}: {impl['exe']} not found")
            return {"exe": exe, "version": self.version([exe])}
        base = self.work / "impl" / slug(impl["name"])
        stamp = base / "stamp.json"
        if stamp.exists():
            return json.loads(stamp.read_text())
        base.mkdir(parents=True, exist_ok=True)
        src = base / "src"
        commit = git_checkout(self.cfg["repos"][impl["kind"]], impl["ref"], src)
        log = base / "build.log"
        env = os.environ.copy()
        extra = [p.format(work=self.work) for p in impl.get("path", [])]
        env["PATH"] = os.pathsep.join(extra + [env["PATH"]])
        print(f"building {impl['name']} ({commit[:10]}), log: {log}", flush=True)
        t0 = time.time()
        info = getattr(self, "build_" + impl["kind"])(impl, base, src, env, log)
        info.update(commit=commit, ref=impl["ref"], build_seconds=round(time.time() - t0))
        stamp.write_text(json.dumps(info, indent=1))
        return info

    def build_cpython(self, impl, base, src, env, log):
        prefix = base / "install"
        env["CC"] = "gcc"
        conf = ["--enable-optimizations", "--with-lto", f"--prefix={prefix}"]
        if impl.get("jit"):
            conf.append("--enable-experimental-jit")
        conf += impl.get("configure", [])
        sh(["./configure", *conf], cwd=src, env=env, log=log)
        make = impl.get("make", [])
        sh(["make", f"-j{JOBS}", *make], cwd=src, env=env, log=log)
        sh(["make", "altinstall", *make], cwd=src, env=env, log=log)
        exe = next(p for p in sorted((prefix / "bin").glob("python[23].*")) if re.fullmatch(r"python\d\.\d+t?", p.name))
        return {"exe": str(exe), "version": self.version([str(exe)])}

    def build_pypy(self, impl, base, src, env, log):
        host = self.build_impl(self.impls[impl["host"]])["exe"]
        goal = src / "pypy" / "goal"
        env["PYPY_USESSION_DIR"] = str(base / "usession")
        os.makedirs(env["PYPY_USESSION_DIR"], exist_ok=True)
        sh([host, "../../rpython/bin/rpython", "--batch", "--opt=jit", "targetpypystandalone.py"], cwd=goal, env=env, log=log)
        exe = next(p for p in goal.glob("pypy*-c") if p.is_file())
        return {"exe": str(exe), "version": self.version([str(exe)])}

    def use_installed_pypy(self, exe):
        """Replace the PyPy builds in the config by an installed PyPy."""
        found = shutil.which(exe)
        if not found:
            raise SystemExit(f"{exe} not found")
        cmd = [found, "-c", "import sys; print('%d.%d.%d' % sys.pypy_version_info[:3])"]
        name = "PyPy " + subprocess.check_output(cmd, text=True).strip()
        impls = {}
        for n, i in self.impls.items():
            if i.get("kind") != "pypy":
                impls[n] = i
            elif name not in impls:
                impls[name] = {"name": name, "exe": found}
        self.impls = impls

    def venv_install(self, base, src, log):
        venv = base / "venv"
        sh([sys.executable, "-m", "venv", venv], log=log)
        sh([venv / "bin" / "pip", "install", "-q", src], log=log)
        return venv / "bin"

    def build_shedskin(self, impl, base, src, env, log):
        bindir = self.venv_install(base, src, log)
        return {"exe": str(bindir / "shedskin"), "flags": impl.get("flags", [])}

    def build_tpy(self, impl, base, src, env, log):
        bindir = self.venv_install(base, src, log)
        return {"exe": str(bindir / "tpyc"), "version": self.version([str(bindir / "tpyc"), "--version"])}

    @staticmethod
    def version(cmd):
        if len(cmd) == 1:
            cmd = cmd + ["-c", "import sys; print(sys.version.replace(chr(10), ' '))"]
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

    # --- program sources

    def source_dir(self, which, program):
        s = self.cfg["sources"][which]
        dest = self.work / "sources" / slug(f"{s['repo']}-{s['ref']}")
        commit = git_checkout(self.cfg["repos"][s["repo"]], s["ref"], dest)
        return dest / s["path"].format(program=program), commit

    def kind(self, impl):
        return self.impls[impl.get("uses", impl["name"])].get("kind", "exe")

    def prepare(self, impl, program, info):
        """Copy the program into a fresh run directory, build it if needed;
        returns the command to time and the sources' commit."""
        kind = self.kind(impl)
        src, commit = self.source_dir("tpy" if kind == "tpy" else "python", program)
        rundir = self.work / "run" / slug(impl["name"]) / program
        log = rundir.parent / f"{program}.build.log"
        flags = [*info.get("flags", []), *self.cfg.get("shedskin_flags", {}).get(program, [])] if kind == "shedskin" else []
        tag = "-".join([info.get("commit", "")[:10], *flags])  # rebuilt when the compiler or flags change
        binary = rundir / "bin" / tag / program
        if kind in ("shedskin", "tpy") and binary.exists():
            return [str(binary)], rundir, commit
        if rundir.exists():
            shutil.rmtree(rundir)
        shutil.copytree(src, rundir)
        script = rundir / f"{program}.py"
        if kind == "shedskin":
            sh([info["exe"], "translate", *flags, script.name], cwd=rundir, log=log)
            sh(["make", f"-j{JOBS}"], cwd=rundir, log=log)
            built = rundir / program
        elif kind == "tpy":
            sh([info["exe"], script.name, "-o", "__tpyc__", "--build"], cwd=rundir, log=log)
            built = next(p for p in (rundir / "__tpyc__").rglob(program) if p.is_file() and os.access(p, os.X_OK))
        else:
            if info.get("version", "").startswith("2."):
                py2ify(script)
            return [info["exe"], script.name], rundir, commit
        binary.parent.mkdir(parents=True)
        shutil.copy2(built, binary)
        return [str(binary)], rundir, commit

    # --- running

    def run(self, impls, programs, force=False):
        timeout = self.cfg.get("timeout", 7200)
        for program in programs:
            for impl in impls:
                res = self.results.setdefault(impl["name"], {})
                if res.get(program, {}).get("times") and "error" not in res[program] and not force:
                    continue
                info = self.build_impl(impl)
                entry = {"times": [], "wall": []}
                try:
                    cmd, rundir, commit = self.prepare(impl, program, info)
                    entry["source_commit"] = commit
                    env = os.environ.copy()
                    env.update(impl.get("env", self.impls[impl.get("uses", impl["name"])].get("env", {})))
                    n = self.cfg["runs"]["compiled" if self.kind(impl) in ("shedskin", "tpy") else "interpreter"]
                    for i in range(n):
                        with open(rundir.parent / f"{program}.out", "w") as out:
                            t0 = time.perf_counter()
                            p = subprocess.run(cmd, cwd=rundir, env=env, stdout=out, stderr=subprocess.STDOUT, timeout=timeout)
                            dt = time.perf_counter() - t0
                        if p.returncode:
                            raise RuntimeError(f"exit status {p.returncode}, see {out.name}")
                        # the programs time their last iterations themselves, after warm-up
                        found = re.findall(r"^TIME ([0-9.]+)$", Path(out.name).read_text(), re.M)
                        if not found:
                            raise RuntimeError(f"no TIME line in output, see {out.name}")
                        entry["times"].append(float(found[-1]))
                        entry["wall"].append(round(dt, 4))
                        print(f"{impl['name']:>20} {program:<14} {float(found[-1]):9.2f}s (wall {dt:.2f}s)", flush=True)
                except Exception as e:  # recorded, so one failure doesn't stop the run
                    entry["error"] = str(e)
                    print(f"{impl['name']:>20} {program:<14} FAILED: {e}", flush=True)
                res[program] = entry
                self.results.setdefault("_meta", {})[impl["name"]] = info
                self.save()

    def list(self):
        """Print each implementation, what it is built from, and its state."""
        rows = [("name", "from", "state", "results")]
        for name, impl in self.impls.items():
            b = self.impls[impl.get("uses", name)]
            if "exe" in b:
                what = b["exe"]
                state = "installed" if shutil.which(b["exe"]) else "not found"
            else:
                what = f"{b['kind']} {b['ref']}"
                stamp = self.work / "impl" / slug(b["name"]) / "stamp.json"
                state = "built " + json.loads(stamp.read_text())["commit"][:10] if stamp.exists() else "not built"
            if "uses" in impl:
                what = f"{impl['uses']} build"
            env = impl.get("env", b.get("env", {}))
            what += "".join(f" {k}={v}" for k, v in env.items())
            done = sum(1 for e in self.results.get(name, {}).values() if e.get("times") and "error" not in e)
            rows.append((name, what, state, f"{done}/{len(self.cfg['programs'])}"))
        widths = [max(len(r[i]) for r in rows) for i in range(3)]
        for r in rows:
            print("  ".join(c.ljust(w) for c, w in zip(r, widths)) + "  " + r[3])

    def report(self, programs, baseline=None):
        names = [n for n in self.impls if n in self.results]
        base = self.results.get(baseline or self.cfg["baseline"], {})
        print(f"{'':20}" + "".join(f"{p:>14}" for p in programs))
        for n in names:
            cells = []
            for p in programs:
                e = self.results[n].get(p)
                if not e or not e["times"]:
                    cells.append("-" if not e else "fail")
                    continue
                t = min(e["times"])
                b = base.get(p, {}).get("times")
                cells.append(f"{t:.2f}s" + (f" {min(b) / t:.1f}x" if b else ""))
            print(f"{n:20}" + "".join(f"{c:>14}" for c in cells))


def py2ify(script):
    """Make a Python 3 program run under 2.7: print function and true division."""
    text = script.read_text()
    tree = ast.parse(text)
    line = 0
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
        line = tree.body[0].end_lineno
    lines = text.splitlines(keepends=True)
    lines.insert(line, "from __future__ import print_function, division\n")
    script.write_text("".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-c", "--config", type=Path, default=HERE / "config.toml")
    ap.add_argument("-w", "--work", type=Path, default=Path.home() / ".cache" / "pybench")
    ap.add_argument("--pypy", metavar="EXE", help="use this installed PyPy (e.g. pypy3) instead of building PyPy")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build implementations")
    b.add_argument("impls", nargs="*")
    r = sub.add_parser("run", help="time programs")
    r.add_argument("-i", "--impl", action="append", help="implementation (repeatable; default all)")
    r.add_argument("-p", "--program", action="append", help="program (repeatable; default all)")
    r.add_argument("-f", "--force", action="store_true", help="re-run programs that have results")
    rep = sub.add_parser("report", help="print times and speedups over the baseline")
    rep.add_argument("-b", "--baseline", help="implementation to compare against (default: from the config)")
    sub.add_parser("list", help="list implementations, and which are built")
    args = ap.parse_args()

    args.work.mkdir(parents=True, exist_ok=True)
    bench = Bench(args.config, args.work.resolve())
    if args.pypy:
        bench.use_installed_pypy(args.pypy)

    def pick(names):
        unknown = [n for n in names or () if n not in bench.impls]
        if unknown:
            raise SystemExit(f"unknown implementation(s): {', '.join(unknown)}; see 'pybench.py list'")
        return [bench.impls[n] for n in (names or bench.impls)]

    programs = getattr(args, "program", None) or bench.cfg["programs"]
    if args.cmd == "build":
        for impl in pick(args.impls):
            print(impl["name"], bench.build_impl(impl))
    elif args.cmd == "run":
        bench.run(pick(args.impl), programs, args.force)
    elif args.cmd == "list":
        bench.list()
    else:
        bench.report(programs, args.baseline)


if __name__ == "__main__":
    main()
