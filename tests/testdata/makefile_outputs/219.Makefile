SHEDSKIN_LIBDIR=/home/fahhem/projects/shedskin/shedskin/shedskin/lib
CC=g++
CCFLAGS=-Wno-deprecated $(CPPFLAGS) -pipe -g -fPIC -D__SS_BIND -I/usr/include/python2.7 -I/usr/include/python2.7 -I. -I${SHEDSKIN_LIBDIR}
LFLAGS=-lgc -lpcre $(LDFLAGS) -shared -Xlinker -export-dynamic -lpthread -ldl  -lutil -lm -lpython2.7


CPPFILES=filename.cpp \
	${SHEDSKIN_LIBDIR}/re.cpp
HPPFILES=filename.hpp \
	${SHEDSKIN_LIBDIR}/re.hpp

all:	main.so


main.so:	$(CPPFILES) $(HPPFILES)
	$(CC) $(CCFLAGS) $(CPPFILES) $(LFLAGS) -o main.so



clean:
	rm -f main.so main.so_prof main.so_debug 
.PHONY: all clean
