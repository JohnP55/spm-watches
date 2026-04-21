import dolphin_memory_engine as dme
import memorywatch

dme.hook()
memorywatch.init_funcs(dme.read_bytes, dme.write_bytes)

pipe_watch = memorywatch.GSWFMemoryWatch("Flipside-Flopside Pipe", 534)
seqpos = memorywatch.get_watch("SequencePosition")
seqpos.write(424)

val = pipe_watch.read()
print(val)

try:
    while 1:
        input("Press enter to toggle the Flipside-Flopside pipe: ")
        pipe_watch.write(not val)
        
        val = pipe_watch.read()
        print(val)
except KeyboardInterrupt:
    dme.un_hook()
