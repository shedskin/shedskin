import pygame
import universe

movie = True

class Display:
    def __init__(self, univ):
        self.univ = univ
        self.window = pygame.display.set_mode((1200, 1200)) 
        self.screen = pygame.display.get_surface() 

    def update(self, ctime):
        univ = self.univ
        my_env = univ.my_env
        landscape = my_env.landscape
        rects = my_env.rects
        update_rects = []
        for i in range(my_env.xsize):
             for j in range(my_env.ysize):
                 obj = landscape[i][j]
                 rect = rects[i][j]
                 update_rects.append(rect)
                 if obj == 0:
                     self.screen.fill((100,0,0), rect)
                 if obj == 1 or obj == 3 or obj ==4:
                     self.screen.fill((0,255,0), rect)
                 if obj == 2:
                     self.screen.fill((0,0,255), rect)
        rects, flat_rects = create_rects(univ.layer_sizes,univ.start_width,univ.lmax)
        display_cells(ctime, self.screen, univ.layer_sizes, univ.spirit_brain, rects, flat_rects)
        update_rects.extend(flat_rects)
        pygame.display.update(update_rects)

def create_rects(layer_sizes,start_width,lmax):
    rects = []
    flat_rects = []
    counter = 0
    layer_width = 0
    layer_depth = 0
    for q,layer in enumerate(layer_sizes):
        for my_iter in range(layer_sizes[q][2]):
            rects.append([])
            if counter == 4:
                #print 'change layer depth'
                layer_depth = layer_depth +layer_sizes[0][0]*16 + 5
                layer_width = 0
                counter = 0
            counter = counter +1
    
            #build one layer
            for i in range(layer[0]):
                rects[-1].append([])
                for j in range(layer[1]):
                    rects[-1][-1].append( ((i*16)+layer_width+start_width,j*16+layer_depth,15,15))
                    if q != lmax-1 or True:
                        flat_rects.append( ((i*16)+layer_width+start_width,j*16+layer_depth,15,15))
            #if q == lmax -1:
                #flat_rects.append( (layer_width+start_width,layer_depth,15*6,15*6))
            layer_width = layer_width + 16*layer[1] + 5
    return rects,flat_rects

def display_cells(ctime, screen, layer_sizes, spirit_brain, rects, flat_rects):
     counter = 0
     for num,layer in enumerate(layer_sizes):
         for k in range(layer[2]):
             for i in range(layer[0]):
                 for j in range(layer[1]):
                     setting = spirit_brain.cell_array[num][i][j][k].network
                     if setting > -0.1:
                        set_spike = True
                     else:
                        set_spike = False

                     color = (setting+1) * 700 
                     if color > 255:
                         color = 255
                     if color <0:
                         color =0 

                     if k ==1:
                         if set_spike:
                             screen.fill((255,0,0),rects[counter][i][j])
                         else:
                             screen.fill((int(color),int(color),200),rects[counter][i][j])
                     else:
                         if set_spike:
                             screen.fill((255,0,0),rects[counter][i][j])
                         else:
                             screen.fill((int(color),int(color),0),rects[counter][i][j])

                     #elif num +2 == lmax and False:

                         #my_rect = pygame.Rect(rects[counter][i][j])
                         #left = (my_rect.left,my_rect.top+my_rect.height/2)
                         #right = (my_rect.right,my_rect.top+my_rect.height/2)
                         #top = (my_rect.left+ my_rect.width/2,my_rect.top)
                         #bottom = (my_rect.left+ my_rect.width/2,my_rect.bottom)
                         #dimond = (top,left,bottom,right)

                         #ex_right = my_rect.width/4
                         #ex_down = my_rect.width/4
                         #if False: # makes dimond
                         #    if i ==0 and j ==0: #north
                         #        dimond = tuple(map(lambda cor: (cor[0]+my_rect.width/2+ex_right,cor[1]-my_rect.width/4+ex_down),dimond))
                         #    if i ==1 and j ==0: #east
                         #        dimond = tuple(map(lambda cor: (cor[0]+my_rect.width/4+ex_right,cor[1]+my_rect.width/2+ex_down),dimond))
                         #    if i ==0 and j ==1: #west
                         #        dimond = tuple(map(lambda cor: (cor[0]-my_rect.width/4+ex_right,cor[1]-my_rect.width/2+ex_down),dimond))
                         #    if i ==1 and j ==1: #south
                         #        dimond = tuple(map(lambda cor: (cor[0]-my_rect.width/2+ex_right,cor[1]+my_rect.width/4+ex_down),dimond))

                         #if set_spike:
                         #    pygame.draw.polygon(screen,(255,0,0),dimond)
                         #else:
                         #    pygame.draw.polygon(screen,(int(color),int(color),0),dimond)

             counter = counter +1

def main():
    if movie:
        pygame.init()

    univ = universe.Universe()
    if movie:
        display = Display(univ)

    print('start calc')
    for ctime in range(2,univ.ttime):
        univ.advance(ctime)
        if movie and ctime%100 == 0:
            display.update(ctime)
        if ctime%10000 == 0:
            print('time: ' + str(ctime) + ' happy: ' + str(univ.happyness))
    print('finish calc')

if __name__ == '__main__':
    main()
