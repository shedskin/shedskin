SHEDSKIN_LIBDIR=/home/fahhem/projects/shedskin/shedskin/shedskin/lib
CC=g++
CCFLAGS=-Wno-deprecated $(CPPFLAGS) -pipe -I. -I${SHEDSKIN_LIBDIR}
LFLAGS=-lgc -lpcre $(LDFLAGS)


CPPFILES=filename.cpp \
	${SHEDSKIN_LIBDIR}/re.cpp
HPPFILES=filename.hpp \
	${SHEDSKIN_LIBDIR}/re.hpp

all:	main


main:	$(CPPFILES) $(HPPFILES)
	$(CC) $(CCFLAGS) $(CPPFILES) $(LFLAGS) -o main.exe

main_prof:	$(CPPFILES) $(HPPFILES)
	$(CC) -pg -ggdb $(CCFLAGS) $(CPPFILES) $(LFLAGS) -o main_prof.exe

main_debug:	$(CPPFILES) $(HPPFILES)
	$(CC) -g -ggdb $(CCFLAGS) $(CPPFILES) $(LFLAGS) -o main_debug.exe


clean:
	rm -f main.exe main_prof.exe main_debug.exe 
.PHONY: all clean
