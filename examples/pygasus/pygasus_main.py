import time
import sys
import pygame
import pygame.image

import pygasus
print(pygasus)

def main(test):
    pygame.init()
    hScreen=pygame.display.set_mode((256,240))
    if test:
        pygasus.read_ines('mario_bros.nes')
    else:
        pygasus.read_ines(sys.argv[1])
    pygasus.pReset()
    pygasus.setkeys({
        'q': pygame.K_q, 'w': pygame.K_w, 'a': pygame.K_a, 's': pygame.K_s,
#        'UP': pygame.K_UP, 'DOWN': pygame.K_DOWN, 'LEFT': pygame.K_LEFT, 'RIGHT': pygame.K_RIGHT, 
    })
    counter = 0
    total = 0
    while True:
        counter += 1
        pygame.event.poll()
        keys=pygame.key.get_pressed()
        pygasus.setkeys2(keys)
        if keys[pygame.K_ESCAPE]: break
        if keys[pygame.K_F11]: pygame.display.toggle_fullscreen()
        if keys[pygame.K_SPACE]: 
            pygame.time.delay(100)
            continue
        if keys[pygame.K_RETURN]:
            pygasus.tpF()
        t0 = time.time()
        pygasus.pExec()
        data = pygasus.getscreen()
        image = pygame.image.frombuffer(data, ( 256, 240 ), 'RGB')
        hScreen.blit(image, (0,0))
        pygame.display.flip()
        hScreen.fill([0,0,0])
        total += (time.time()-t0)
        if not test and counter % 60 == 0:
            print('FPS:', 60/total)
            total = 0
        if test and counter == 2000:
            break

if __name__ == '__main__':
   main(len(sys.argv) > 1 and sys.argv[1] == 'test')
