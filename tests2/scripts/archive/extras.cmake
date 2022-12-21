
set(CPP_HEADERS
    ${SHEDSKIN_LIBDIR}/array.hpp
    ${SHEDSKIN_LIBDIR}/binascii.hpp
    ${SHEDSKIN_LIBDIR}/bisect.hpp
    ${SHEDSKIN_LIBDIR}/builtin.hpp
    ${SHEDSKIN_LIBDIR}/collections.hpp
    ${SHEDSKIN_LIBDIR}/colorsys.hpp
    ${SHEDSKIN_LIBDIR}/configparser.hpp
    ${SHEDSKIN_LIBDIR}/copy.hpp
    ${SHEDSKIN_LIBDIR}/csv.hpp
    ${SHEDSKIN_LIBDIR}/datetime.hpp
    ${SHEDSKIN_LIBDIR}/fnmatch.hpp
    ${SHEDSKIN_LIBDIR}/functools.hpp
    ${SHEDSKIN_LIBDIR}/gc.hpp
    ${SHEDSKIN_LIBDIR}/getopt.hpp
    ${SHEDSKIN_LIBDIR}/glob.hpp
    ${SHEDSKIN_LIBDIR}/heapq.hpp
    ${SHEDSKIN_LIBDIR}/io.hpp
    ${SHEDSKIN_LIBDIR}/itertools.hpp
    ${SHEDSKIN_LIBDIR}/math.hpp
    ${SHEDSKIN_LIBDIR}/mmap.hpp
    ${SHEDSKIN_LIBDIR}/random.hpp
    ${SHEDSKIN_LIBDIR}/re.hpp
    ${SHEDSKIN_LIBDIR}/select.hpp
    ${SHEDSKIN_LIBDIR}/signal.hpp
    ${SHEDSKIN_LIBDIR}/socket.hpp
    ${SHEDSKIN_LIBDIR}/stat.hpp
    ${SHEDSKIN_LIBDIR}/string.hpp
    ${SHEDSKIN_LIBDIR}/struct.hpp
    ${SHEDSKIN_LIBDIR}/sys.hpp
    ${SHEDSKIN_LIBDIR}/time.hpp

    # builtin
    ${SHEDSKIN_LIBDIR}/builtin/bool.hpp
    ${SHEDSKIN_LIBDIR}/builtin/bytes.hpp
    ${SHEDSKIN_LIBDIR}/builtin/complex.hpp
    ${SHEDSKIN_LIBDIR}/builtin/exception.hpp
    ${SHEDSKIN_LIBDIR}/builtin/file.hpp
    ${SHEDSKIN_LIBDIR}/builtin/format.hpp
    ${SHEDSKIN_LIBDIR}/builtin/function.hpp
    ${SHEDSKIN_LIBDIR}/builtin/math.hpp
    ${SHEDSKIN_LIBDIR}/builtin/str.hpp

    # os
    ${SHEDSKIN_LIBDIR}/os/__init__.hpp
    ${SHEDSKIN_LIBDIR}/os/path.hpp
)

set(CPP_SOURCES
    ${SHEDSKIN_LIBDIR}/array.cpp
    ${SHEDSKIN_LIBDIR}/binascii.cpp
    ${SHEDSKIN_LIBDIR}/bisect.cpp
    ${SHEDSKIN_LIBDIR}/builtin.cpp
    ${SHEDSKIN_LIBDIR}/collections.cpp
    ${SHEDSKIN_LIBDIR}/colorsys.cpp
    ${SHEDSKIN_LIBDIR}/configparser.cpp
    ${SHEDSKIN_LIBDIR}/copy.cpp
    ${SHEDSKIN_LIBDIR}/csv.cpp
    ${SHEDSKIN_LIBDIR}/datetime.cpp
    ${SHEDSKIN_LIBDIR}/fnmatch.cpp
    ${SHEDSKIN_LIBDIR}/functools.cpp
    ${SHEDSKIN_LIBDIR}/gc.cpp
    ${SHEDSKIN_LIBDIR}/getopt.cpp
    ${SHEDSKIN_LIBDIR}/glob.cpp
    ${SHEDSKIN_LIBDIR}/heapq.cpp
    ${SHEDSKIN_LIBDIR}/io.cpp
    ${SHEDSKIN_LIBDIR}/itertools.cpp
    ${SHEDSKIN_LIBDIR}/math.cpp
    ${SHEDSKIN_LIBDIR}/mmap.cpp
    ${SHEDSKIN_LIBDIR}/random.cpp
    ${SHEDSKIN_LIBDIR}/re.cpp
    ${SHEDSKIN_LIBDIR}/select.cpp
    ${SHEDSKIN_LIBDIR}/signal.cpp
    ${SHEDSKIN_LIBDIR}/socket.cpp
    ${SHEDSKIN_LIBDIR}/stat.cpp
    ${SHEDSKIN_LIBDIR}/string.cpp
    ${SHEDSKIN_LIBDIR}/struct.cpp
    ${SHEDSKIN_LIBDIR}/sys.cpp
    ${SHEDSKIN_LIBDIR}/time.cpp

    # builtin
    ${SHEDSKIN_LIBDIR}/builtin/bool.cpp
    ${SHEDSKIN_LIBDIR}/builtin/bytes.cpp
    ${SHEDSKIN_LIBDIR}/builtin/complex.cpp
    ${SHEDSKIN_LIBDIR}/builtin/exception.cpp
    ${SHEDSKIN_LIBDIR}/builtin/file.cpp
    ${SHEDSKIN_LIBDIR}/builtin/format.cpp
    ${SHEDSKIN_LIBDIR}/builtin/function.cpp
    ${SHEDSKIN_LIBDIR}/builtin/math.cpp
    ${SHEDSKIN_LIBDIR}/builtin/str.cpp

    # os
    ${SHEDSKIN_LIBDIR}/os/__init__.cpp
    ${SHEDSKIN_LIBDIR}/os/path.cpp
)