# The part of subprocess the game uses (Popen with stdin PIPE or DEVNULL,
# stdout and stderr DEVNULL, .stdin.write/flush, poll, kill, wait), over
# os.fork and os.execvpe, for the Shedskin build. One difference: poll()
# returns NO_STATUS instead of None while the process runs, as Shedskin
# cannot mix None and int; prep.py rewrites the game's two `is None`
# tests of poll() results.
import os
import signal

INHERIT = 0  # None in subprocess, which Shedskin cannot mix with ints
PIPE = -1
DEVNULL = -3
NO_STATUS = -(1 << 62)


class _Pipe:
    def __init__(self, fd):
        self.fd = fd
        self.closed = False

    def write(self, data):
        n = 0
        while n < len(data):
            n += os.write(self.fd, data[n:])
        return n

    def flush(self):
        pass

    def close(self):
        if not self.closed:
            self.closed = True
            os.close(self.fd)


def _redirect(how, fd, pipe_fd):
    if how == PIPE:
        os.dup2(pipe_fd, fd)
    elif how == DEVNULL:
        null = os.open(os.devnull, os.O_RDWR)
        os.dup2(null, fd)


class Popen:
    def __init__(self, args, stdin=INHERIT, stdout=INHERIT, stderr=INHERIT):
        self.args = args
        self.returncode = NO_STATUS
        self.stdin = None
        stdin_r = stdin_w = -1
        if stdin == PIPE:
            stdin_r, stdin_w = os.pipe()
        # close-on-exec, so it reads empty once the exec has worked
        err_r, err_w = os.pipe()
        pid = os.fork()
        if pid == 0:
            try:
                # the game blocks SIGTERM and SIGHUP, and exec would keep them blocked
                signal.pthread_sigmask(signal.SIG_SETMASK, [])
                _redirect(stdin, 0, stdin_r)
                _redirect(stdout, 1, -1)
                _redirect(stderr, 2, -1)
                os.execvpe(args[0], args, os.environ)
            except OSError as e:
                os.write(err_w, str(e).encode())
            os._exit(255)
        os.close(err_w)
        if stdin_r >= 0:
            os.close(stdin_r)
        error = os.read(err_r, 1024)
        os.close(err_r)
        if len(error) > 0:
            os.waitpid(pid, 0)
            if stdin_w >= 0:
                os.close(stdin_w)
            raise OSError(error.decode())
        self.pid = pid
        if stdin_w >= 0:
            self.stdin = _Pipe(stdin_w)

    def _status(self, status):
        self.returncode = os.waitstatus_to_exitcode(status)
        if self.stdin is not None:
            self.stdin.close()

    def poll(self):
        if self.returncode == NO_STATUS:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if pid == self.pid:
                self._status(status)
        return self.returncode

    def wait(self):
        if self.returncode == NO_STATUS:
            pid, status = os.waitpid(self.pid, 0)
            self._status(status)
        return self.returncode

    def send_signal(self, sig):
        if self.returncode == NO_STATUS:
            os.kill(self.pid, sig)

    def terminate(self):
        self.send_signal(signal.SIGTERM)

    def kill(self):
        self.send_signal(signal.SIGKILL)
