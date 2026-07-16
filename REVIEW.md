# Shed Skin Code-Generation Review

**Scope.** How Shed Skin turns (restricted) Python 3 into C++, and the quality and performance of the C++ it emits. The focus is the generator (`shedskin/cpp.py`, `typestr.py`, `virtual.py`, `extmod.py`) and the runtime library the generated code calls into (`shedskin/lib/`), because emitted-code performance is a joint product of the two. Type-inference *correctness* (integer overflow, container specialization, etc.) is covered by a separate review and only cross-referenced here. Throughout, three distinct concerns are kept separate because they have different owners and fixes: the **generation process** (what `cpp.py` decides to emit while lowering the AST), **emitted-code quality** (the textual quality of that C++), and **runtime-library performance** (`shedskin/lib/`, which the emitted code links against and which bounds speed independently of the generator). Section 3 is organized on exactly this axis.

**Method.** Direct reading of the generator and runtime, plus **empirical inspection of real emitted C++**: several representative Python programs were compiled with `shedskin translate` and the resulting `.cpp` read line-by-line and recompiled with `g++ -std=c++17 -Wall -Wextra` to observe warnings. Findings tagged **[verified]** were confirmed against emitted output or a compile; **[code]** were read in the compiler/runtime source with `file:line` citations.

**Version.** 0.9.12, branch `master`.

---

## 1. How code is generated

The pipeline is a whole-program, type-directed, single-pass emitter:

```
graph.parse_module   -> constraint graph from the Python AST      (graph.py)
infer.analyze        -> whole-program type inference (CPA + IFA)   (infer.py)
cpp.generate_code    -> emit C++ per module from the typed AST     (cpp.py)
typestr.*            -> render inferred type-sets as C++ types     (typestr.py)
makefile / cmake     -> build emitted C++ against shedskin/lib     (the runtime)
```

**Two-pass per module** (`cpp.py:4467-4479`). For each module a `ConstVisitor` (`cpp.py:148-170`) first walks the AST to intern string/bytes literals into `const_N` globals, then a `GenerateVisitor` (`cpp.py:176`) emits the `.cpp` (`module_cpp`, `cpp.py:572-721`) and `.hpp` (`module_hpp`, `cpp.py:430-492`). `insert_extras` (`cpp.py:251-263`) post-splices includes and forward declarations.

**Visitor dispatch.** Both visitors subclass a hand-rolled `BaseNodeVisitor` (`ast_utils.py:142-179`) dispatching on `visit_<NodeClass>` with `*args` threading the current `(func, class)` context. There is no separate expression/statement IR: statements manage indentation and `;` via `start`/`output`/`eol` (`cpp.py:357-373`); expressions accrete text onto `self.line` via `append`/`visitm` (`cpp.py:363-391`). Every emission decision keys off the inferred type-set in `self.mergeinh` (`= gx.merged_inh`), with `connector()` (`cpp.py:393-400`) choosing `::` / `.` / `->` and `typestr.unboxable()` deciding native operator vs boxed method call.

**Type rendering** (`typestr.typestrnew`, `typestr.py:287-509`) collapses an inferred set of `(class, contour)` pairs to a *single* C++ type by a lowest-common-parent computation (`lowest_common_parents`, `typestr.py:126-165`). When a program point has a real union it widens to an abstract base pointer (`pyiter<T>*`, `pyseq<T>*`, `pyobj*`) and emits upcasts; numeric unions widen to `float`/`complex` (`typestr.py:365-404`). A single concrete class renders to a zero-overhead static type; scalars in `{int,float,bool,complex}` render to unboxed values (`__ss_int`, `__ss_float`, `complex`).

**Memory model.** Every object is a Boehm-GC heap pointer (`pyobj : public gc`, `builtin.hpp:131`); containers are the STL with GC allocators — `list<T>` is `std::vector` (`list.hpp:5-7`), `str` is `std::basic_string` (`str.hpp:6-11`), `dict`/`set` are `std::unordered_map`/`std::unordered_set` (`builtin.hpp:244-249`). Scalars are stored by value in their concrete C++ type; there is **no runtime boxing of ints/floats and no `PyObject` header** — the single biggest structural advantage over CPython.

---

## 2. What the generator does well

The generator is mature and applies a solid set of loop-shape and container-construction optimizations. These are worth stating because the recommendations below should not regress them.

- **Loop specialization.** `for i in range(...)` becomes a native `FAST_FOR` macro (`ast_utils.py:91-97`, `cpp.py:1399-1427`) rather than a heap iterator. Dedicated fast paths exist for `enumerate`, `zip`, `dict` iteration, file iteration, and iterating a literal list/tuple via C++11 braced-init range-for (`cpp.py:1496-1622`).

- **Comprehension pre-sizing.** A comp over a literal `range(N)` or a sized container emits `__ss_result->resize(N)` and writes by index instead of `append()` (`cpp.py:3883-3941`). **[verified]** — a `[x*x for x in range(100)]` compiled to `resize(100)` + `units[__4] = x*x`.

- **Compile-time default arguments.** `f(x, y=10, z=20)` called as `f(1)` emits `f(1, 10, 20)` — defaults resolved at the call site, zero runtime cost. **[verified]**

- **Constant interning.** Single-char string/byte literals map to shared `__char_cache` / `__byte_cache` globals rather than allocating (`cpp.py:229-249`, `builtin.cpp:92-104`); integer-to-string has a chunked digit cache (`str.cpp:748-786`); `''.join(list)` is a single pre-sized allocation (`str.hpp:153-203`).

- **Expression-level fast paths.** `a+b+c...` string chains fold to one `__add_strs` (`cpp.py:2347-2358`); `list + [elt]` avoids a temporary list (`cpp.py:2493-2505`); `t[0]`/`t[1]` on a 2-tuple become `__getfirst__`/`__getsecond__` (`cpp.py:2997-3011`); `x in range(...)` becomes arithmetic with no iteration (`cpp.py:2537-2555`).

- **Unboxed scalars + native arithmetic.** `+ - *` on ints/floats emit raw C++ operators (`cpp.py:2469-2480`, `math.hpp:169-174`); `list<__ss_int>` stores raw machine ints. This is why numeric/array code approaches hand-written C++.

- **Conservative, usage-driven virtualization.** A method is made `virtual` only when it is actually called on a polymorphic receiver *and* a subclass redefines it (`virtual.py:125-198`). Single-implementation hierarchies stay non-virtual and inlinable.

---

## 3. Missed optimizations and low-quality emission, grouped by locus

These findings have three different owners and fixes, and are grouped accordingly; within each group they are ordered by impact. Each is backed by emitted output or a source citation.

- **3A. Generation process** -- decisions `cpp.py` makes while lowering the AST; the fix lives in the generator.

- **3B. Runtime-library performance** -- `shedskin/lib/`, which the emitted code links against; these bound speed regardless of what `cpp.py` emits, and most are fixable without touching the generator.

- **3C. Emitted-code quality** -- textual quality of the produced C++ (redundancy, readability, warnings); little runtime effect, but relevant to the stated goal of readable output.

### 3A. Generation process

#### 3A.1 No fusion of reducers over generator expressions -- HIGHEST IMPACT [verified] [IMPLEMENTED]

`sum(s.area() for s in shapes)` does **not** compile to an accumulation loop. It compiles to a heap-allocated iterator *class* deriving from `__iter<T>`, with captured variables, an `int __last_yield` state field, and a `goto`-based state machine, which `__sum` then drives by **virtual `__get_next()` dispatch per element**:

```cpp
class list_comp_0 : public __iter<__ss_float> { ... int __last_yield; ... };
__ss_float list_comp_0::__get_next() {
    if(!__last_yield) goto __after_yield_0;
    __last_yield = 0;
    FOR_IN(s,shapes,0,2,3)
        __result = s->area();
        return __result;
        __after_yield_0:;
    END_FOR
    __stop_iteration = true; ...
}
...
return __sum(new list_comp_0(shapes));   // heap alloc + virtual call per element
```

There is no code path recognizing `reducer(genexpr)` for `sum`/`any`/`all`/`min`/`max` and lowering it to a direct loop (`cpp.py:2896-2960`, `3681-3945`). Every such idiom pays a heap allocation, a vtable indirection per element, and a `goto` state machine, where the equivalent hand C++ is a register accumulator over an inlined vector loop. This is the single largest structural inefficiency in ordinary Python style, and it is the idiomatic way to write reductions.

**Fix.** Special-case `sum/any/all/min/max/"".join` with a single `GeneratorExp`/comp argument: inline the comp body directly into an accumulator loop at the call site (the machinery already exists — `FAST_FOR`/`FOR_IN` plus the resize/reserve logic).

**Status: implemented for `sum`/`any`/`all`/`min`/`max` over a generator expression** (`cpp.py`, `compute_fused_reducers`/`reducer_func`/`emit_reducer_call`). A `reducer(<genexpr>)` call now lowers to a `static inline` accumulator function (no heap allocation, no virtual `__get_next()`, no `goto` state machine); `sum` fuses only for a numeric accumulator, `min`/`max` replicate the runtime's first-element fold and `ValueError`-on-empty, and any non-matching call (e.g. `min`/`max` with `key=`/`default=`, or the varargs form) falls back to the previous path. Verified against CPython (fused + fallback + empty-sequence cases), full unit suite (246 passed), and `mypy --strict` clean.

`"".join` was investigated and deliberately **not** fused: `str::join` already materializes its argument into a pre-sized buffer in one pass, so coercing the genexpr to a list just materializes twice and nets ~0 (measured 0.97x on a realistic format-and-join workload). See `reducer-benchmark.md`. The bracketed `reducer([listcomp])` form remains a possible follow-up. Benchmarks: `tests/benchmarks/reducer_bench.py` gives ~41x for `sum`/`min`/`max` and ~6.5x for `any`/`all` when the reducer is the hot loop; within noise on the example programs that use the pattern only in cold paths (`sunfish`, `sat`).

#### 3A.2 `%` and `/` always emit the floored-semantics helpers [code, verified]

`x % k` always emits `__mods(x,k)` and `x / k` (true div) `__divs`, unconditionally (`cpp.py:2427-2442`), where `__mods`/`__divs` carry sign-correction branches for Python's floored semantics (`math.hpp:124-134`, `103-115`). When both operands are provably non-negative (e.g. a `range` loop variable mod a positive constant) the native `%`/`/` matches Python exactly and is a single instruction. The authors flagged this themselves: `# XXX C++ knows %, /, so we can overload?` (`cpp.py:2426`). A sign/range analysis on the operands would let the common non-negative case use native operators.

### 3B. Runtime-library performance

#### 3B.1 String concatenation in a loop is O(n^2), for both `+` and `+=` -- HIGH IMPACT [verified]

`str::__add__` allocates a fresh buffer and copies both operands every call (`str.cpp:503-511`), and `str::__iadd__` merely forwards to it (`str.cpp:512-514`). So:

```cpp
FAST_FOR(i,0,n,1,0,1)
    s = (s)->__iadd__(const_1);   // new allocation + full copy each iteration
END_FOR
```

Building a string of length *n* by repeated concatenation is quadratic; `+=` gives no relief because Python string immutability is enforced by always returning a new object. The runtime *has* an in-place `operator+=(const char*)` (`str.cpp:90-96`) but it is used only internally, never for user `+=`.

**Fix (two options).** (a) Emit a mutable accumulator when inference proves the target is not aliased across the loop (the reassignment `s = s + ...` is detectable) and reuse the buffer in place. (b) Recognize the accumulation pattern and lower to a `''.join(...)`-style pre-sized build. Either turns a common O(n^2) idiom into O(n). The runtime already has a fast `join`; the gap is purely codegen not routing to it.

#### 3B.2 `dict`/`set` use `std::unordered_map`/`std::unordered_set` -- HIGH IMPACT [code]

`dict` wraps `std::unordered_map` and `set` wraps `std::unordered_set` (`dict.hpp:45`, `set.hpp:24`, `builtin.hpp:244-249`) -- chaining hashtables that allocate one node per element and chase pointers on every probe. This is the classic slow choice: poor cache locality and per-insert allocation, materially behind CPython's compact open-addressed dict and far behind a modern flat/open-addressing table (e.g. `absl::flat_hash_map`, `robin_hood`, `ankerl::unordered_dense`). For dict/set-churn-heavy programs this is the dominant runtime ceiling. Scalar keys are otherwise cheap (unboxed, direct `std::hash`, value compare -- `hash.hpp:16-38`, `compare.hpp:5-21`); object keys pay a virtual `__hash__`/`__eq__` per probe.

**Fix.** Swap the `__GC_DICT`/`__GC_SET` aliases to a header-only open-addressing map with a GC-aware allocator. This is a localized change (two typedefs plus API shims) with a potentially large, broad speedup and no generator changes.

#### 3B.3 Bounds/wrap checks on every subscript unless globally disabled [code]

Every `list`/`str`/`tuple` subscript routes through `__wrap` (`builtin.hpp:217-227`): a negative-index normalization branch plus a bounds-check branch (both `__builtin_expect(...,0)`), on by default. `__getfast__` -- the variant emitted when the compiler believes access is safe -- **still calls `__wrap`**, so the checks are only removed with a whole-program `-D__SS_NOBOUNDS`/`-D__SS_NOWRAP`. There is no per-access proof (e.g. a `FAST_FOR` index known in `[0,len)`) that elides the check locally.

**Fix.** When inference/loop-shape proves an index is in range and non-negative (the common `for i in range(len(x))` and comprehension-index cases), emit a genuine unchecked access instead of `__getfast__`-that-still-wraps.

#### 3B.4 Generic iteration uses C++ exceptions for `StopIteration` [code]

The default `__iter<T>::__next__` protocol signals end-of-iteration by throwing (`builtin.hpp:426-431`), which the header itself labels "(slow) exception handling" and works around with `__get_next`/`__stop_iteration` (`builtin.hpp:273`, `433-440`). Concrete containers avoid this via the `for_in_*` traits, but any iteration over an abstract `pyiter<T>*` (including the genexpr classes of 3A.1) can land on the exception path.

### 3C. Emitted-code quality

#### 3C.1 Redundant / warning-generating emission [verified]

Compiling the generated `.cpp` with `-Wall -Wextra` produces a steady stream of warnings that reflect genuinely redundant emitted code:

- **Self-assignment in tuple unpacking.** `for a,b in pairs` emits `__0 = __0;` (`-Wself-assign`) before the element extraction -- a literal no-op (`cpp.py` unpack path around `3377-3412`). **[verified]**

- **Dead local temporaries.** Iterator scratch temps (`__iter<T> *__1`, etc.) are declared for every loop even when the specialized macro never uses them, and comp variables left in the parent scope after hoisting are still declared, e.g. an unused `void *s;` (`local_defs`, `cpp.py:3801-3814`, with no liveness check). Multiple `-Wunused-variable` per function. **[verified]**

- **Unused catch variables.** `except E as e:` emits `catch (E *e)` even when `e` is unused (`cpp.py:1348-1352`), yielding `-Wunused-parameter`. The no-name form `catch (E *)` already exists but is used only when the source omits the name. **[verified]**

- **Redundant static tuple-arity check.** Unpacking a statically-typed `tuple<__ss_int>` (arity known at compile time) still emits a runtime `__SS_UNPACK_CHECK(__0, 2)` every iteration. **[verified]**

None of these are correctness bugs, but they are dead code the C++ optimizer must strip and noise that buries real warnings. A `-Wall`-clean generator is achievable: skip self-assigns, run a use-check before declaring locals, omit unused catch names (or tag `[[maybe_unused]]`), and drop the unpack check when arity is statically known.

#### 3C.2 Literal and constant handling [verified / code]

- **Every integer literal is wrapped `__ss_int(...)`** (`cpp.py:4440-4445`), including array indices, loop bounds, and `resize` counts; negatives become `(-__ss_int(1))`. Purely so a `LL` suffix can attach in 64/128-bit mode. Harmless after optimization but a large source of visual noise.

- **`"__main__"` is allocated twice.** `module_cpp` emits `__name__ = new str("__main__")` through a hardcoded path (`cpp.py:648`) that bypasses the const cache, while the user's `if __name__ == "__main__"` interns the same literal as a separate `const_N` (`cpp.py:237`). Result: two identical `new str("__main__")` allocations in essentially every program. **[verified]** Const interning is also strictly per-module -- identical literals across modules are never shared.

- **Constant small-integer powers** rely on a runtime branch in an `inline` `__power` (`math.hpp:11-14`, `20-30`); with a literal exponent the C++ compiler folds it, so this is adequate, not a real miss.

#### 3C.3 Emitted-C++ quality: no `const`, references, or move semantics [code]

The generator emits essentially no `const` (grepping emitted strings yields none), never uses references except for one comprehension capture-by-ref (`cpp.py:3733`), and uses no `std::move`/rvalue refs (consistent with the GC-pointer model but it means inline value tuples are default-copied). Control flow is macro-based (`FAST_FOR`, `FOR_IN`, `WITH`), literals are `__ss_int(...)`-wrapped, and everything is heavily parenthesized (`(((a+b)))`), so output is functional but hard to read. `NULL` is used rather than `nullptr`; no `constexpr`. None of this affects performance after `-O2`, but it lowers the debuggability of generated code -- a stated Shed Skin use case is reading the C++.

---

## 4. Build configuration [code]

Generated builds use `-O2 -march=native` (Makefile, `makefile.py:672-729`) or `-O2` (CMake, `fn_add_shedskin_product.cmake:391`). Notably absent:

- **No `-flto`.** Because each module is its own translation unit, cross-module inlining (e.g. small methods, `__init__`) does not happen. Whole-program transpilers benefit strongly from LTO; offering it would be a low-effort, broad win.

- **No `-O3` option.** The runtime is template/`inline`-heavy; `-O3`'s extra inlining and vectorization can matter for numeric kernels. Worth exposing as a flag (measure per benchmark; `-O3` is not universally faster).

- **No PGO path.** For the target use case (a few hundred lines run at max speed), a profile-guided second build is a natural, high-value option to document/automate.

The runtime headers themselves also emit warnings under `-Wall -Wextra` (deprecated `sprintf` at `math.hpp:291`, unused vars at `math.hpp:230`/`393`) and carry a latent quality bug: `set`'s variadic constructor sets `__class__ = cl_dict` instead of `cl_set` (`set.hpp:199`). **[verified / code]**

---

## 5. Prioritized recommendations

| # | Change | Impact | Effort | Where |
|---|--------|--------|--------|-------|
| 1 | Fuse `sum/any/all/min/max/join` over a genexpr/comp into a direct accumulator loop | High (removes heap alloc + per-element virtual dispatch on an idiomatic pattern) | Med | `cpp.py:2896-2960`, `3681-3945` |
| 2 | Replace `std::unordered_map/set` with an open-addressing table | High (broad dict/set speedup) | Low-Med | `builtin.hpp:244-249` + API shims |
| 3 | Lower string `+`/`+=` accumulation to in-place/join when target is non-aliased | High (O(n^2) -> O(n)) | Med | `cpp.py` assign path + `str.cpp:503-514` |
| 4 | Elide bounds/wrap checks per-access when index provably in range | Med (hot subscripts) | Med | `builtin.hpp:217-227`, `__getfast__` emission |
| 5 | Native `%`/`/` when operands provably non-negative | Med | Med | `cpp.py:2427-2442` |
| 6 | Make the generator `-Wall`-clean: drop `__0=__0`, dead locals, unused catch names, static-arity unpack checks | Low perf / high hygiene | Low | `cpp.py:1348-1352`, `3377-3412`, `3801-3814` |
| 7 | Dedup `"__main__"` and share consts cross-module | Low | Low | `cpp.py:237`, `648` |
| 8 | Offer `-flto`, `-O3`, and a PGO build path | Med (multi-module programs) | Low | `makefile.py`, cmake resources |
| 9 | Fix runtime warnings and the `set` `__class__ = cl_dict` bug | Correctness/hygiene | Low | `set.hpp:199`, `math.hpp:230/291/393` |

**Framing.** Items 1-3 are the substantive performance work; each targets a *structural* inefficiency (heap-iterator reductions, chaining hashtables, quadratic string build) rather than a micro-optimization, and each is idiomatic Python that a user would not expect to be slow. Items 6-7 are cheap credibility/readability wins given a stated goal of readable generated C++. The generator's numeric/array code path is already close to hand-written C++ and should be left alone.

---

## 6. Caveats and alternative framing

- Several "inefficiencies" are *correctness* requirements, not oversights: `__mods`/`__divs` branches implement Python's floored semantics; string immutability forbids naive in-place `+=` without an aliasing proof. The recommendations above are guarded on exactly those proofs; where inference cannot establish them, the current conservative emission is correct and must stay.

- The dict/set swap (item 2) is the highest-leverage change *if* real workloads are dict/set-bound. That is an empirical question -- the `examples/` benchmark suite should be measured before and after, since some programs are entirely list/int-bound and would see no change. All impact ratings here are analytical, not yet benchmarked; a measurement pass over `examples/` under `asv` would convert them to evidence.

- This review deliberately excludes type-inference correctness (integer overflow, silent wraparound, container-type divergence), which is the subject of the companion correctness review; those are the more dangerous class of issue (silent wrong output) but orthogonal to the code-generation quality assessed here.
