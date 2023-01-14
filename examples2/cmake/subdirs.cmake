# add_subdirectory(TarsaLZP)
# add_subdirectory(TonyJpegDecoder)
if(LINUX)
	add_subdirectory(WebServer) ## select not working on macOS
endif()
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
# add_subdirectory(minilight) # nested exe
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
add_subdirectory(tictactoe)
add_subdirectory(timsort)
add_subdirectory(voronoi)
add_subdirectory(voronoi2)
add_subdirectory(yopyra)
