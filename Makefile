# project variables
SHEDSKIN_LIBDIR=$(CURDIR)/shedskin/lib
CPPFILES=$(GENERATED_CPPFILES) $(BUILTIN_CPPFILES)
HPPFILES=$(GENERATED_HPPFILES) $(BUILTIN_HPPFILES)

INCLUDEDIRS=-I$(CURDIR) -I$(SHEDSKIN_LIBDIR) -I/usr/include -I/usr/local/include
LINKDIRS=-L/usr/lib -L/usr/local/lib

CXX=g++
CXXFLAGS+=-O2 -std=c++17 -march=native $(CPPFLAGS) -D__SS_INT64 $(INCLUDEDIRS)
LDFLAGS+= $(LINKDIRS)
LDLIBS=-lgc -lgctba -lutil

BUILTIN_CPPFILES=$(SHEDSKIN_LIBDIR)/builtin.cpp
BUILTIN_HPPFILES=$(SHEDSKIN_LIBDIR)/builtin.hpp
GENERATED_CPPFILES=$(CURDIR)/test.cpp
GENERATED_HPPFILES=$(CURDIR)/test.hpp

.PHONY: all clean

all: test

test: $(CPPFILES) $(HPPFILES)
	$(CXX)  $(CXXFLAGS) $(CPPFILES) $(LDLIBS) $(LDFLAGS) -o test

test_debug: $(CPPFILES) $(HPPFILES)
	$(CXX) -g -ggdb $(CXXFLAGS) $(CPPFILES) $(LDLIBS) $(LDFLAGS) -o test_debug

test_prof: $(CPPFILES) $(HPPFILES)
	$(CXX) -pg -ggdb $(CXXFLAGS) $(CPPFILES) $(LDLIBS) $(LDFLAGS) -o test_prof

clean:
	@rm -rf test test_prof test_debug

reset: clean
	@rm -f $(GENERATED_CPPFILES) $(GENERATED_HPPFILES)

