cmake_minimum_required(VERSION 3.19)

project(shedskin_examples LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

set(DEBUG off)

set(SHEDSKIN ${PROJECT_SOURCE_DIR}/../../shedskin)
set(SHEDSKIN_LIB ${SHEDSKIN}/shedskin/lib)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/_cmake)

option(AS_EXT "build/run python extension examples")
option(NO_BOUNDS "enable no bounds checking")

if(NO_BOUNDS)
    set(OPT_B "-b")
else()
    set(OPT_B "")
endif()

include_directories(
    ${SHEDSKIN_LIB}
)

link_directories(
    /usr/local/lib
)

find_package(Python COMPONENTS Interpreter Development)
if(DEBUG)
    message("python:" ${Python_EXECUTABLE})
    message("python_include" ${Python_INCLUDE_DIRS})
endif()

include(fn_add_shedskin_example)
include(fn_add_shedskin_exe_example)
include(fn_add_shedskin_ext_example)
include(fn_copy_to_build_dir)


# -----------------------------------------------------------------------
# copy test data to cmake 'build' folder

file(COPY ${PROJECT_SOURCE_DIR}/testdata DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

# -----------------------------------------------------------------------
# add examples by subdirectory


add_subdirectory(ac_encode)
add_subdirectory(adatron)
add_subdirectory(amaze)
add_subdirectory(ant)
add_subdirectory(astar) # ext
add_subdirectory(bh)
add_subdirectory(block)
add_subdirectory(brainfuck)
# add_subdirectory(c64)
add_subdirectory(chaos)
add_subdirectory(chess)
add_subdirectory(chull)
add_subdirectory(circle) # ext
add_subdirectory(dijkstra)
add_subdirectory(dijkstra2)
add_subdirectory(fysphun) # ext
add_subdirectory(genetic)
add_subdirectory(genetic2)
add_subdirectory(go)
# add_subdirectory(gs)
add_subdirectory(hq2x)
add_subdirectory(kanoodle)
add_subdirectory(kmeanspp)
add_subdirectory(life)
add_subdirectory(linalg)
add_subdirectory(loop)
add_subdirectory(mandelbrot)
add_subdirectory(mandelbrot2) # ext
add_subdirectory(mao)
# add_subdirectory(mastermind) # nested ext
add_subdirectory(mastermind2)
add_subdirectory(minilight) # nested exe
add_subdirectory(minpng)
# add_subdirectory(msp_ss) # requires serial
add_subdirectory(mwmatching)
add_subdirectory(nbody)
add_subdirectory(neural1)
add_subdirectory(neural2)
add_subdirectory(oliva2)
add_subdirectory(othello)
add_subdirectory(path_tracing)
add_subdirectory(pisang)
add_subdirectory(plcfrs)
add_subdirectory(pygasus) # ext no-bounds
add_subdirectory(pygmy)
add_subdirectory(pylife) # ext
# add_subdirectory(pylot) # nested exe
add_subdirectory(pystone)
add_subdirectory(quameon) # deep exe
add_subdirectory(rdb)
add_subdirectory(richards)
# add_subdirectory(rsync) # requires hashlib
add_subdirectory(rubik)
add_subdirectory(rubik2)
add_subdirectory(sat)
add_subdirectory(score4)
# add_subdirectory(sha) # requires hashlib
add_subdirectory(sieve)
add_subdirectory(sokoban)
add_subdirectory(solitaire)
add_subdirectory(stereo) # ext
add_subdirectory(sudoku1)
add_subdirectory(sudoku2)
add_subdirectory(sudoku3)
add_subdirectory(sudoku4)
add_subdirectory(sudoku5)
add_subdirectory(sunfish)
# add_subdirectory(tarsalzp)
add_subdirectory(tictactoe)
add_subdirectory(timsort)
# add_subdirectory(tonyjpeqdecoder)
add_subdirectory(voronoi)
add_subdirectory(voronoi2)
if(LINUX)
    add_subdirectory(webserver) ## select not working on macOS
endif()
add_subdirectory(yopyra)



