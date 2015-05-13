SHEDSKIN_LIBDIR=/home/fahhem/projects/shedskin/shedskin/shedskin/lib
CC=g++
CCFLAGS=-Wno-deprecated $(CPPFLAGS) -pipe -I/home/fahhem/.virtualenvs/shedskin\include -D__SS_BIND -I. -I$(SHEDSKIN_LIBDIR)
LFLAGS=-lgc -lpcre $(LDFLAGS) /dll /libpath:/home/fahhem/.virtualenvs/shedskin\libs 


CPPFILES=filename.cpp \
	$(SHEDSKIN_LIBDIR)/re.cpp
HPPFILES=filename.hpp \
	$(SHEDSKIN_LIBDIR)/re.hpp

all:	main.pyd


main.pyd:	$(CPPFILES) $(HPPFILES)
	$(CC) $(CCFLAGS) $(CPPFILES) $(LFLAGS) /out: main.pyd

clean:
	rm -f main.pyd 
.PHONY: all clean
