SHEDSKIN_LIBDIR=/home/fahhem/projects/shedskin/shedskin/shedskin/lib
CC=g++
CCFLAGS=-Wno-deprecated $(CPPFLAGS) -pipe -I. -I$(SHEDSKIN_LIBDIR)
LFLAGS=-lgc -lpcre $(LDFLAGS)


CPPFILES=filename.cpp \
	$(SHEDSKIN_LIBDIR)/re.cpp
HPPFILES=filename.hpp \
	$(SHEDSKIN_LIBDIR)/re.hpp

all:	main


main:	$(CPPFILES) $(HPPFILES)
	$(CC) $(CCFLAGS) $(CPPFILES) $(LFLAGS) /out: main.exe

clean:
	rm -f main.exe 
.PHONY: all clean
