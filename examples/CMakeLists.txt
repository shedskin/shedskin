cmake_minimum_required(VERSION 3.18.4)

project(shedskin_products LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

# -----------------------------------------------------------------------------
# options

option(DEBUG "Enable debug output" OFF)

option(BUILD_EXECUTABLE "Build executable" ON)
option(BUILD_EXTENSION "Build python extension" OFF)
option(BUILD_TEST "Build test" ON)

option(ENABLE_SPM "Enable shedskin dependency management" OFF)
option(ENABLE_CONAN "Enable conan for dependency management" OFF)
option(ENABLE_EXTERNAL_PROJECT "Enable ExternalProject for dependency mgmt" OFF)

# -----------------------------------------------------------------------------
# find python executable and shedskin package path

find_package(Python REQUIRED COMPONENTS Interpreter Development)
if(DEBUG)
    message("python:" ${Python_EXECUTABLE})
    message("python_include:" ${Python_INCLUDE_DIRS})
endif()

# -----------------------------------------------------------------------------
# find shedskin package path

if(NOT DEFINED SHEDSKIN)
    execute_process(
        COMMAND ${Python_EXECUTABLE} -c "from shedskin import pkg_path; pkg_path()"
        OUTPUT_VARIABLE SHEDSKIN_PATH
        COMMAND_ERROR_IS_FATAL ANY
    )
    set(SHEDSKIN ${SHEDSKIN_PATH} CACHE PATH "setting path to shedskin pkg" FORCE)
endif()

set(SHEDSKIN_LIB ${SHEDSKIN}/lib)

include_directories(
    ${SHEDSKIN_LIB}
)

# -----------------------------------------------------------------------------
# dependency mgmt solutions

if(ENABLE_SPM)
    set(SPM_DEPS ${CMAKE_BINARY_DIR}/deps)
    set(SPM_LIB_DIRS ${SPM_DEPS}/lib)
    set(SPM_INCLUDE_DIRS ${SPM_DEPS}/include)

elseif(ENABLE_CONAN)
    find_program(CONAN conan)
    if(NOT CONAN)
        message(FATAL_ERROR "conan not found, install with `pip install conan`")
    endif()
    include(${CMAKE_BINARY_DIR}/conan_paths.cmake)
    find_package(BDWgc)
    find_package(PCRE)

elseif(ENABLE_EXTERNAL_PROJECT)
    set(install_dir ${CMAKE_CURRENT_BINARY_DIR}/install)
    include(ExternalProject)
    ExternalProject_Add(
        bdwgc
        INSTALL_DIR    ${install_dir}
        GIT_REPOSITORY https://github.com/ivmai/bdwgc.git
        GIT_TAG        d0ba209660ea8c663e06d9a68332ba5f42da54ba
        CMAKE_ARGS     -DCMAKE_INSTALL_PREFIX:PATH=${install_dir}
                       -DBUILD_SHARED_LIBS=OFF
                       -Denable_cplusplus=ON
    )
    ExternalProject_Add(
        pcre
        INSTALL_DIR    ${install_dir}
        URL            https://sourceforge.net/projects/pcre/files/pcre/8.45/pcre-8.45.tar.gz
        URL_MD5        01b80f8177ab91da63e7e5c5d5dfcb83
        CMAKE_ARGS     -DCMAKE_INSTALL_PREFIX:PATH=${install_dir}
    )
endif()


# -----------------------------------------------------------------------------
# includes
list(APPEND CMAKE_MODULE_PATH "${SHEDSKIN}/resources/cmake")
include(utils)
include(fn_add_shedskin_product)

# -----------------------------------------------------------------------
# any 'test_*' folders are automatically treated as tests

if(BUILD_TEST)
    enable_testing()
    if (EXISTS ${PROJECT_SOURCE_DIR}/testdata)
        # copy test data to cmake 'build' folder
        file(COPY ${PROJECT_SOURCE_DIR}/testdata DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    endif()

    # add_subdirectory(tests)
    file(GLOB test_dirs "test_*"
        LIST_DIRECTORIES true
    )

    foreach(testdir ${test_dirs})
        if(IS_DIRECTORY ${testdir})
            get_filename_component(testdir_name ${testdir} NAME_WLE)
            if (DEBUG)
                message("testdir_name:" ${testdir_name})
            endif()
            add_subdirectory(${testdir_name})
        endif()
    endforeach()
endif()


# -----------------------------------------------------------------------
# add subdirectories here

add_subdirectory(ac_encode)
add_subdirectory(adatron)
add_subdirectory(amaze)
add_subdirectory(ant)
add_subdirectory(astar) # ext
add_subdirectory(bh)
add_subdirectory(block)
add_subdirectory(brainfuck)
#add_subdirectory(c64) works locally, fix in CI!
add_subdirectory(chaos)
add_subdirectory(chess)
add_subdirectory(chull)
add_subdirectory(circle) # ext
add_subdirectory(collatz)
add_subdirectory(dijkstra)
add_subdirectory(dijkstra2)
add_subdirectory(doom)
add_subdirectory(fysphun) # ext
add_subdirectory(genetic)
add_subdirectory(genetic2)
add_subdirectory(go)
add_subdirectory(gs)
add_subdirectory(kanoodle)
add_subdirectory(kmeanspp)
add_subdirectory(life)
add_subdirectory(linalg)
add_subdirectory(loop)
add_subdirectory(lz2)
add_subdirectory(mandelbrot)
add_subdirectory(mandelbrot2) # ext
add_subdirectory(mao)
add_subdirectory(mastermind) # nested ext
add_subdirectory(mastermind2)
add_subdirectory(minilight)
add_subdirectory(minpng)
add_subdirectory(mwmatching)
add_subdirectory(nbody)
add_subdirectory(neural1)
add_subdirectory(neural2)
add_subdirectory(oliva2)
add_subdirectory(othello)
add_subdirectory(othello2)
add_subdirectory(path_tracing)
add_subdirectory(pisang)
add_subdirectory(plcfrs)
add_subdirectory(pygasus) # ext no-bounds
add_subdirectory(pygmy)
add_subdirectory(pylife) # ext
add_subdirectory(pylot) # nested ext
add_subdirectory(pystone)
add_subdirectory(quameon) # deep exe
add_subdirectory(rdb)
add_subdirectory(richards)
add_subdirectory(rubik)
add_subdirectory(rubik2)
add_subdirectory(sat)
add_subdirectory(score4)
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
add_subdirectory(tarsalzp)
add_subdirectory(tictactoe)
add_subdirectory(timsort)
add_subdirectory(tonyjpegdecoder)
add_subdirectory(voronoi)
add_subdirectory(voronoi2)
if(${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
    ## select not working on macOS (win?)
    ## windows not yet tested.
    add_subdirectory(webserver)
#    add_subdirectory(msp_ss) # requires serial
#    add_subdirectory(rsync) # requires hashlib (openssl)
    add_subdirectory(hq2x) # check windows issue
#    add_subdirectory(sha) # requires hashlib (openssl)
endif()
add_subdirectory(yopyra)
