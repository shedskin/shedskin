 #does not support multi-player

import random
#{
import pygame
#}

class Enviroment:
    def __init__(self,xsize,ysize,num_food,movie,food_type,dist_type):
        #1 norm food
        #2 creature
        #0 blank
        #3 horz food
        #4 vert food
        self.movie = movie
        self.landscape = [ [0 for x in range(ysize)] for y in range(xsize)]
        self.xsize = xsize
        self.ysize = ysize
        self.food_type = food_type
        #self.face =pygame.image.load("smile.jpeg")
        self.update_rects = []

        #{
        if self.movie:
            pass
            self.set_up_display()
        #}

        if dist_type == "hetero":
            for i in range(num_food/2):
                self.gen_vert_obj()

            for i in range(num_food/2):
                self.gen_horz_obj()

        if dist_type == "homo":
            for i in range(num_food):
                self.gen_object(1)

        self.critx, self.crity = self.gen_object(2)


    def update_land(self,obj,x,y):
        self.landscape[x][y] = obj
#{
        if self.movie:
            if obj == 0:
                self.screen.fill((100,0,0),self.rects[x][y])
                self.update_rects.append(self.rects[x][y])
            if obj == 1 or obj == 3 or obj ==4:
                self.screen.fill((0,255,0),self.rects[x][y])
                self.update_rects.append(self.rects[x][y])
            if obj == 2:
                #self.screen.blit(self.face,(x,y),(10,10,5,5))
                self.screen.fill((0,0,255),self.rects[x][y])
                self.update_rects.append(self.rects[x][y])
  #}          

    def gen_vert_obj(self):
        while True:
            x = random.randint(0, self.xsize - 1 )
            y = random.randint(0,self.ysize-3)
            if self.landscape[x][y] == 0 and self.landscape[x][y+1] == 0:
                self.update_land(4,x,y)
                self.update_land(4,x,y+1)
                return x,y

    def gen_horz_obj(self):
        while True:
            x = random.randint(0, self.xsize - 3 )
            y = random.randint(0,self.ysize-1)
            if self.landscape[x][y] == 0 and self.landscape[x+1][y] == 0:
                self.update_land(3,x,y)
                self.update_land(3,x+1,y)
                return x,y


    def gen_object(self,obj):
        while True:
            x = random.randint(0, self.xsize - 1 )
            y = random.randint(0,self.ysize-1)
            if self.landscape[x][y] == 0:
                self.update_land(obj,x,y)
                return x,y
    
    def wrap_calc(self,x,y):
        while x >= self.xsize:
            x = x- self.xsize
        while x< 0:
            x = x + self.xsize
        while y >= self.ysize:
            y = y- self.ysize
        while y< 0:
            y = y + self.ysize
        return x,y


    def teleport(self):
        while True:
            new_x = random.randint(0,self.xsize-1)
            new_y = random.randint(0,self.ysize-1)
            if self.landscape[new_x][new_y] == 0:
                self.update_land(2,new_x,new_y)
                self.update_land(0,self.critx,self.crity)
                self.critx = new_x
                self.crity = new_y
                return

    def move_crit(self,direction):
        if direction=='north':
            newcrit=(self.critx,self.crity-1)
            newcrit=self.wrap_calc(newcrit[0],newcrit[1])
        if direction=='south':
            newcrit=(self.critx,self.crity+1)
            newcrit=self.wrap_calc(newcrit[0],newcrit[1])
        if direction=='east':
            newcrit=(self.critx+1,self.crity)
            newcrit=self.wrap_calc(newcrit[0],newcrit[1])
        if direction=='west':
            newcrit=(self.critx-1,self.crity)
            newcrit=self.wrap_calc(newcrit[0],newcrit[1])

        if direction=='north_west':
            newcrit=(self.critx-1,self.crity-1)
            newcrit=self.wrap_calc(newcrit[0],newcrit[1])
        if direction=='south_west':
            newcrit=(self.critx-1,self.crity+1)
            newcrit=self.wrap_calc(newcrit[0],newcrit[1])
        if direction=='north_east':
            newcrit=(self.critx+1,self.crity-1)
            newcrit=self.wrap_calc(newcrit[0],newcrit[1])
        if direction=='south_east':
            newcrit=(self.critx+1,self.crity+1)
            newcrit=self.wrap_calc(newcrit[0],newcrit[1])
        if direction=='null':
            newcrit=(self.critx,self.crity)
            newcrit=self.wrap_calc(newcrit[0],newcrit[1])


        self.update_land(0,self.critx,self.crity)
        self.critx = newcrit[0]
        self.crity = newcrit[1]
        if self.landscape[self.critx][self.crity]==1:
            self.update_land(2,self.critx,self.crity)
            self.gen_object(1)
            return "bacon"

        
        if self.landscape[self.critx][self.crity]==3:
            self.update_land(2,self.critx,self.crity)
            if self.landscape[self.critx+1][self.crity] == 3:
                self.update_land(0,self.critx+1,self.crity)
            if self.landscape[self.critx-1][self.crity] == 3:
                self.update_land(0,self.critx-1,self.crity)
            self.gen_horz_obj()
            if self.food_type == "horz":
                return "bacon"
            else:
                return "grass"


        if self.landscape[self.critx][self.crity]==4:
            self.update_land(2,self.critx,self.crity)
            if self.landscape[self.critx][self.crity+1] == 4:
                self.update_land(0,self.critx,self.crity+1)
            if self.landscape[self.critx][self.crity-1] == 4:
                self.update_land(0,self.critx,self.crity-1)
            self.gen_vert_obj()
            if self.food_type == "vert":
                return "bacon"
            else:
                return "grass"

        self.update_land(2,self.critx,self.crity)
        return "blank"

        
    def get_vision(self,xloc, yloc,x_range,y_range):
        xloc = xloc - x_range
        yloc = yloc - y_range
        array = []
        for i in range((x_range*2)+1):
            array.append([])
            for j in range((y_range*2)+1):
                wxloc,wyloc = self.wrap_calc(xloc+i,yloc+j)
                array[i].append(self.landscape[wxloc][wyloc])
        return array

#{
    def set_up_display(self):
         self.window = pygame.display.set_mode((1200, 1200)) 
         self.screen = pygame.display.get_surface() 
         self.rects = []
         self.clock = pygame.time.Clock()
         for i in range(self.xsize):
            self.rects.append([])
            for j in range(self.ysize):
                 self.rects[i].append( (i*6,j*6,5,5))
 
         for i in range(self.xsize):
             for j in range(self.ysize):
                 self.screen.fill((100,0,0),self.rects[i][j])
                 self.update_rects.append(self.rects[i][j])



    def display(self,extra_rects):
         self.clock.tick(10000)
         self.update_rects.extend(extra_rects)
         pygame.display.update(self.update_rects)
         self.update_rects = []
#}


    
        
        
