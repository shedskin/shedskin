
set(CPP_HEADERS
    ${SHEDSKIN_LIB}/array.hpp
    ${SHEDSKIN_LIB}/binascii.hpp
    ${SHEDSKIN_LIB}/bisect.hpp
    ${SHEDSKIN_LIB}/builtin.hpp
    ${SHEDSKIN_LIB}/collections.hpp
    ${SHEDSKIN_LIB}/colorsys.hpp
    ${SHEDSKIN_LIB}/configparser.hpp
    ${SHEDSKIN_LIB}/copy.hpp
    ${SHEDSKIN_LIB}/csv.hpp
    ${SHEDSKIN_LIB}/datetime.hpp
    ${SHEDSKIN_LIB}/fnmatch.hpp
    ${SHEDSKIN_LIB}/functools.hpp
    ${SHEDSKIN_LIB}/gc.hpp
    ${SHEDSKIN_LIB}/getopt.hpp
    ${SHEDSKIN_LIB}/glob.hpp
    ${SHEDSKIN_LIB}/heapq.hpp
    ${SHEDSKIN_LIB}/io.hpp
    ${SHEDSKIN_LIB}/itertools.hpp
    ${SHEDSKIN_LIB}/math.hpp
    ${SHEDSKIN_LIB}/mmap.hpp
    ${SHEDSKIN_LIB}/random.hpp
    ${SHEDSKIN_LIB}/re.hpp
    # ${SHEDSKIN_LIB}/select.hpp
    ${SHEDSKIN_LIB}/signal.hpp
    ${SHEDSKIN_LIB}/socket.hpp
    ${SHEDSKIN_LIB}/stat.hpp
    ${SHEDSKIN_LIB}/string.hpp
    ${SHEDSKIN_LIB}/struct.hpp
    ${SHEDSKIN_LIB}/sys.hpp
    ${SHEDSKIN_LIB}/time.hpp

    # builtin
    ${SHEDSKIN_LIB}/builtin/bool.hpp
    ${SHEDSKIN_LIB}/builtin/bytes.hpp
    ${SHEDSKIN_LIB}/builtin/complex.hpp
    ${SHEDSKIN_LIB}/builtin/exception.hpp
    ${SHEDSKIN_LIB}/builtin/file.hpp
    ${SHEDSKIN_LIB}/builtin/format.hpp
    ${SHEDSKIN_LIB}/builtin/function.hpp
    ${SHEDSKIN_LIB}/builtin/math.hpp
    ${SHEDSKIN_LIB}/builtin/str.hpp

    # os
    ${SHEDSKIN_LIB}/os/__init__.hpp
    ${SHEDSKIN_LIB}/os/path.hpp
)

set(CPP_SOURCES
    ${SHEDSKIN_LIB}/array.cpp
    ${SHEDSKIN_LIB}/binascii.cpp
    ${SHEDSKIN_LIB}/bisect.cpp
    ${SHEDSKIN_LIB}/builtin.cpp
    ${SHEDSKIN_LIB}/collections.cpp
    ${SHEDSKIN_LIB}/colorsys.cpp
    ${SHEDSKIN_LIB}/configparser.cpp
    ${SHEDSKIN_LIB}/copy.cpp
    ${SHEDSKIN_LIB}/csv.cpp
    ${SHEDSKIN_LIB}/datetime.cpp
    ${SHEDSKIN_LIB}/fnmatch.cpp
    ${SHEDSKIN_LIB}/functools.cpp
    ${SHEDSKIN_LIB}/gc.cpp
    ${SHEDSKIN_LIB}/getopt.cpp
    ${SHEDSKIN_LIB}/glob.cpp
    ${SHEDSKIN_LIB}/heapq.cpp
    ${SHEDSKIN_LIB}/io.cpp
    ${SHEDSKIN_LIB}/itertools.cpp
    ${SHEDSKIN_LIB}/math.cpp
    ${SHEDSKIN_LIB}/mmap.cpp
    ${SHEDSKIN_LIB}/random.cpp
    ${SHEDSKIN_LIB}/re.cpp
    # ${SHEDSKIN_LIB}/select.cpp
    ${SHEDSKIN_LIB}/signal.cpp
    ${SHEDSKIN_LIB}/socket.cpp
    ${SHEDSKIN_LIB}/stat.cpp
    ${SHEDSKIN_LIB}/string.cpp
    ${SHEDSKIN_LIB}/struct.cpp
    ${SHEDSKIN_LIB}/sys.cpp
    ${SHEDSKIN_LIB}/time.cpp

    # builtin
    ${SHEDSKIN_LIB}/builtin/bool.cpp
    ${SHEDSKIN_LIB}/builtin/bytes.cpp
    ${SHEDSKIN_LIB}/builtin/complex.cpp
    ${SHEDSKIN_LIB}/builtin/exception.cpp
    ${SHEDSKIN_LIB}/builtin/file.cpp
    ${SHEDSKIN_LIB}/builtin/format.cpp
    ${SHEDSKIN_LIB}/builtin/function.cpp
    ${SHEDSKIN_LIB}/builtin/math.cpp
    ${SHEDSKIN_LIB}/builtin/str.cpp

    # os
    ${SHEDSKIN_LIB}/os/__init__.cpp
    ${SHEDSKIN_LIB}/os/path.cpp
)