from enum import Enum
from typing import Any
import struct

# Initialized at runtime when hooked. These are used to access the proper addresses.
game_region = 'P'
game_revision = 0

def read_placeholder(addr: int, len: int) -> bytes:
    raise NotImplementedError("Read function was not defined. Please call init_funcs() with the proper read/write functions (ex. pydme, NetMemoryAccess_client, etc.)")

def write_placeholder(addr:int, data: bytes) -> None:
    raise NotImplementedError("Write function was not defined. Please call init_funcs() with the proper read/write functions (ex. pydme, NetMemoryAccess_client, etc.)")

read_func = read_placeholder
write_func = write_placeholder

def init_funcs(readfunc, writefunc):
    global read_func
    global write_func

    read_func = readfunc
    write_func = writefunc

class Datatype(Enum):
    BYTE = 1
    HALFWORD = 2
    WORD = 3
    FLOAT = 4
    DOUBLE = 5
    STRING = 6
    BYTEARRAY = 7
    BOOL = 8
    VOIDPTR = 9

class Endianness(Enum):
    BIG = '>'
    LITTLE = '<'

# TODO: maybe change this from a config? not really useful unless someone uses this for non-Wii games for some reason. if you're reading this in 2035 and are planning to use this on anything other than a Wii game (if this even ever gets used for anything other than SPM), feel free to open an issue.
endian = Endianness.BIG

class MemoryWatch:
    def __init__(self, name: str, address: int, datatype: Datatype) -> None:
        self.name = name
        self.address = address
        self.datatype = datatype

    @staticmethod
    def read_and_unpack(address: int, fmt: str, size: int) -> Any:
        return struct.unpack(endian.value + fmt, read_func(address, size))[0]

    @staticmethod
    def pack_and_write(address: int, data: bytes, fmt: str) -> None:
        write_func(address, struct.pack(endian.value + fmt, data))

    @staticmethod
    def read_byte(address:int) -> int:
        return MemoryWatch.read_and_unpack(address, "b", 1)

    @staticmethod
    def read_halfword(address:int) -> int:
        return MemoryWatch.read_and_unpack(address, "h", 2)

    @staticmethod
    def read_word(address:int) -> int:
        return MemoryWatch.read_and_unpack(address, "i", 4)

    @staticmethod
    def read_float(address:int) -> int:
        return MemoryWatch.read_and_unpack(address, "f", 4)

    @staticmethod
    def read_double(address:int) -> int:
        return MemoryWatch.read_and_unpack(address, "d", 8)

    @staticmethod
    def read_string(address:int) -> int:
        s = ""
        i = 0
        cur_char = ""
        while (cur_char := chr(read_func(address+i, 1))) != '\0':
            s += cur_char
            i += 1
        return s
    
    @staticmethod
    def read_bool(address: int) -> bool:
        return not not MemoryWatch.read_byte(address)

    @staticmethod
    def write_byte(address: int, value: int) -> None:
        value &= 0xff
        MemoryWatch.pack_and_write(address, value, 'b')

    @staticmethod
    def write_halfword(address: int, value: int) -> None:
        value &= 0xffff
        MemoryWatch.pack_and_write(address, value, 'h')

    @staticmethod
    def write_word(address: int, value: int) -> None:
        value &= 0xffffffff
        MemoryWatch.pack_and_write(address, value, 'i')

    @staticmethod
    def write_float(address: int, value: float) -> None:
        MemoryWatch.pack_and_write(address, value, 'f')

    @staticmethod
    def write_double(address: int, value: float) -> None:
        MemoryWatch.pack_and_write(address, value, 'd')

    @staticmethod
    def write_string(address: int, value: str) -> None:
        for i,e in enumerate(value):
            MemoryWatch.pack_and_write(address + i, ord(e))
        MemoryWatch.pack_and_write(address + len(value), 0) # add the null terminator at the end

    @staticmethod
    def write_bool(address: int, value: bool) -> None:
        MemoryWatch.write_byte(address, int(value))

    _accessor_methods = {
        Datatype.BYTE: (read_byte, write_byte),
        Datatype.HALFWORD: (read_halfword, write_halfword),
        Datatype.WORD: (read_word, write_word),
        Datatype.FLOAT: (read_float, write_float),
        Datatype.DOUBLE: (read_double, write_double),
        Datatype.STRING: (read_string, write_string),
        Datatype.BOOL: (read_bool, write_bool),
    }

    def get_accessors(self):
        return MemoryWatch._accessor_methods[self.datatype]

    def read(self):
        if self.datatype == Datatype.BYTEARRAY:
            return read_func(self.address, self.len)
        return self.get_accessors()[0](self.address)
    
    def write(self, value):
        if isinstance(value, Enum):
            value = value.value
        self.get_accessors()[1](self.address, value)

class ByteArrayMemoryWatch(MemoryWatch):
    def __init__(self, name: str, address: int, size: int = 0) -> None:
        super().__init__(name, address, Datatype.BYTEARRAY)
        self.size = size
    
    def read(self) -> bytes:
        return read_func(self.address, self.size)
    
    def write(self, value: bytes):
        self.size = len(value)
        write_func(self.address, value)

class BitFieldMemoryWatch(MemoryWatch):
    def __init__(self, name: str, address: int, datatype: Datatype, bitmask: int = 0):
        super().__init__(name, address, datatype)
        self.bitmask = bitmask
    
    def read(self) -> bool:
        return self.get_accessors()[0](self.address) & self.bitmask == self.bitmask
    
    def write(self, value: bool) -> None:
        accessors = self.get_accessors()
        res = accessors[0](self.address)
        if value:
            res |= self.bitmask
        else:
            res &= ~self.bitmask
        accessors[1](self.address, res)

from watch_defs import watches

def get_address(name: str) -> int:
    return watches[name]["addresses"][game_region][game_revision]

def get_watch(name: str) -> MemoryWatch:
    watch_def = watches[name]
    address = get_address(name)
    if watch_def["datatype"] == Datatype.BYTEARRAY:
        return ByteArrayMemoryWatch(address, watch_def["size"])
    return MemoryWatch(name, address, watch_def["datatype"])

class GSWFMemoryWatch(BitFieldMemoryWatch):
    def __init__(self, name: str, gswf_id: int) -> None:
        q,r = divmod(gswf_id, 32)
        super().__init__(name, get_address("GSWF_base_address") + q*4, Datatype.WORD, 1 << r)
