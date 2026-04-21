# spm-watches
This is an old Python utility I made for Flash's SPMMulti project in 2023. It hasn't been used in a while, but now that there are plans to do shared-stats runs again, I've decided to update and formally release this.

It was originally made only with Dolphin in mind, but since people want to do shared-stats runs on console, I've updated it to work using any read/write function provided by the user (for instance, SPMNetMemoryAccess's client script).

This utility has *not* been tested on console, that is left as an exercise to the reader.

# How to use
The provided test script `testmw.py` demonstrates a sample usage with PyDolphinMemoryEngine, allowing you to toggle on/off the blue pipe connecting Flipside and Flopside with Enter.

Before running, you may add memory watches in `watch_defs.py` using the format provided there.

At runtime, you must initialize the read/write functions using `memorywatch.init_funcs()`.

To get a watch from `watch_defs.py`, you can do `seqpos = memorywatch.get_watch("SequencePosition")`.

To read the value from a watch, you can do `seqpos.read()`.

To write the value to a watch, you can do `seqpos.write(424)`.
