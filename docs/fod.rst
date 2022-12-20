Frequently occurring discussions
================================

My god, why?
------------

Because we can!

But I heard we can't! Type inference doesn't scale! it's exponential…
---------------------------------------------------------------------

Does the graph published `here <http://shed-skin.blogspot.fr/2010/12/shed-skin-07-type-inference-scalability.html>`__ look exponential? Since publishing it, the largest program has almost doubled in size, and it still fits this (slightly quadratic?) curve.

Type inference for arbitrary python code may be intractable, but that doesn't say anything about statically restricted programs. There just hasn't been much research on the topic in recent years, and failed experiments from way back still seem to linger in people's minds. There have been real improvements though, and computers are infinitely faster these days.

The perceived problem is also somewhat academic, because one could observe most types in a running python program (or store analysis results of a previous session), making type inference much easier. shedskin doesn't do this, because so far it's not needed.

But still, a JIT compiler is easier to use, and just as fast.
-------------------------------------------------------------

shedskin makes a different trade-off than the typical JIT compiler. Rather than try and give a good speedup for arbitrary python code, it is a tool that explicitly sacrifices some flexibility in order to maximize performance for certain types of programs. This may make it useless in many cases, and useful in some.

It is very useful to have a good JIT compiler when writing, say, a Django application. But when you are writing a neural network implementation, for example, it is not easy for a JIT to come close to the performance of a static C++ compiler. `Here <http://attractivechaos.github.io/plb/>`__ is an interesting performance comparison between different python implementions. Note that the first two tests can run a lot faster still when using 'shedskin -b'.

Static compilation has other advantages. If you know what you are doing, for example, it is more transparent how your code is optimized. Static typing also gives you a guarantee of type-correctness - compilation with shedskin sometimes actually uncovers bugs in the original code.

No sir, I don't like it. Restricted python is not python!
---------------------------------------------------------

Code accepted by shedskin is still pure python code. You can still develop/debug it with CPython, and use more than 20 common standard library modules. The `shedskin example test set <https://github.com/shedskin/shedskin/tree/master/examples>`_ shows that a statically restricted subset of python can still be quite useful.

Shedskin can also generate extension modules for you, that can be incorporated into larger python programs. So you can use unrestricted python code and arbitrary libraries in your main program, but still get a speedup in some critical piece of code, while keeping everything in pure python.

For example, the `pylot raytracer example <https://github.com/shedskin/shedskin/tree/master/examples/pylot>`_ uses Tk and multiprocessing in combination with a shedskin-compiled extension module, and the `c64 emulator example <https://github.com/shedskin/shedskin/tree/master/examples/c64>`_ uses pygtk for its interface.

If you want to have ultimate performance, use manual C
------------------------------------------------------

True, but:

* not everyone can program in C
* not everyone likes to program in C
* not every program can be made much faster in C
* statically compiled python code can often be fast enough
* a single python version is easier to debug and maintain

Well, almost true, because you will have to use assembly language for ultimate performance of course.

But wait, those JIT compilers will be faster than manual assembly language!
---------------------------------------------------------------------------

That's of course ridiculous. but it's true JITs will probably be 'fast enough' in more and more cases, so it's just not worth it to spend time optimizing things further. shedskin is there to push performance further if needed, with potentially much less user effort than having to resort to manual C.

Integration is not straightforward
----------------------------------

shedskin has its own implementation of the python builtins, so when objects are passed between shedskin and cpython, they often have to be converted, which can be very slow indeed. Additionally, not every type of object can be passed. For example, numpy is currently not supported, so numpy arrays have to be passed via their 'tolist' method.

shedskin is a tool, that can be very useful at times, but often you'll have to puzzle a bit how to best use it in a given situation.

My program doesn't become faster after compilation
--------------------------------------------------

In most cases, this is because C++ is not faster at IO, allocating small objects or string operations. there's often no use in compiling a program for speed if one of these is the bottleneck.

Working around small object allocations can often make the resulting C++ much faster. See the :ref:`documentation <performance-tips>` for other performance tips.

shedskin doesn't terminate for my program
-----------------------------------------

We'd really like to hear about such programs, as they can be very useful to improve shedskin's type inference engine. Please post them on the `mailing list <https://groups.google.com/forum/#!forum/shedskin-discuss>`_.

shedskin is known to have trouble analyzing actually dynamic types. First please make sure that you are not mixing different types together, such as integers and strings in the same list or variable.

If you are not sure where the dynamic types come from, try to compile a small version of your program first, and add to it, until you see which part of the code triggers them.

What about parallellization?
----------------------------

The preferred way to parallelize shedskin-compiled programs is to generate a single extension module (shedskin -e), and use this in combination with the multiprocessing library. This way, the original program will also run faster than when using threads (no issues with the Global Interpreter Lock).

See the `pylot raytracer example <https://github.com/shedskin/shedskin/tree/master/examples/pylot>`_ for an example of this.

What about MSVC?
----------------

Occasionally, patches are committed to improve support for MSVC. It is not officially supported, however.

Several modules will probably not work very well, especially the 'os' module.

Patches to improve support for MSVC `are welcome <https://github.com/shedskin/shedskin/pulls>`_.
