# By Daniel Rosengren, modified
#   http://www.timestretch.com/FractalBenchmark.html
# See also vectorized Python+Numeric+Pygame version:
#   http://www.pygame.org/pcr/mandelbrot/index.php

def mandelbrot(max_iterations=1000):
    bailout = 16
    for y in xrange(-39, 39):
        line = []
        for x in xrange(-39, 39):
            cr = y/40.0 - 0.5
            ci = x/40.0
            zi = 0.0
            zr = 0.0
            i = 0
            while True:
                i += 1
                temp = zr * zi
                zr2 = zr * zr
                zi2 = zi * zi
                zr = zr2 - zi2 + cr
                zi = temp + temp + ci
                if zi2 + zr2 > bailout:
                    line.append(" ")
                    break
                if i > max_iterations:
                    line.append("#")
                    break
        print "".join(line)

for x in range(10):
    mandelbrot()

