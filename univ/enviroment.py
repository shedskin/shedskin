 #does not support multi-player

import random

class Enviroment:
    def __init__(self,xsize,ysize,num_food,food_type,dist_type):
        #1 norm food
        #2 creature
        #0 blank
        #3 horz food
        #4 vert food
        self.landscape = [ [0 for x in range(ysize)] for y in range(xsize)]
        self.xsize = xsize
        self.ysize = ysize
        self.food_type = food_type

        if dist_type == "hetero":
            for i in range(num_food/2):
                self.gen_vert_obj()

            for i in range(num_food/2):
                self.gen_horz_obj()

        if dist_type == "homo":
            for i in range(num_food):
                self.gen_object(1)

        self.critx, self.crity = self.gen_object(2)

        self.rects = []

        for i in range(self.xsize):
            self.rects.append([])
            for j in range(self.ysize):
                 self.rects[i].append( (i*6,j*6,5,5))

    def update_land(self,obj,x,y):
        self.landscape[x][y] = obj

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
    
    def wrap_calc_x(self,x):
        while x >= self.xsize:
            x = x- self.xsize
        while x< 0:
            x = x + self.xsize
        return x

    def wrap_calc_y(self,y):
        while y >= self.ysize:
            y = y- self.ysize
        while y< 0:
            y = y + self.ysize
        return y

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
            new_critx = self.wrap_calc_x(self.critx)
            new_crity = self.wrap_calc_y(self.crity-1)
        if direction=='south':
            new_critx = self.wrap_calc_x(self.critx)
            new_crity = self.wrap_calc_y(self.crity+1)
        if direction=='east':
            new_critx = self.wrap_calc_x(self.critx+1)
            new_crity = self.wrap_calc_y(self.crity)
        if direction=='west':
            new_critx = self.wrap_calc_x(self.critx-1)
            new_crity = self.wrap_calc_y(self.crity)

        if direction=='north_west':
            new_critx = self.wrap_calc_x(self.critx-1)
            new_crity = self.wrap_calc_y(self.crity-1)
        if direction=='south_west':
            new_critx = self.wrap_calc_x(self.critx-1)
            new_crity = self.wrap_calc_y(self.crity+1)
        if direction=='north_east':
            new_critx = self.wrap_calc_x(self.critx+1)
            new_crity = self.wrap_calc_y(self.crity-1)
        if direction=='south_east':
            new_critx = self.wrap_calc_x(self.critx+1)
            new_crity = self.wrap_calc_y(self.crity+1)

        if direction=='null':
            new_critx = self.wrap_calc_x(self.critx)
            new_crity = self.wrap_calc_y(self.crity)

        self.update_land(0,self.critx,self.crity)
        self.critx = new_critx
        self.crity = new_crity
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
                wxloc,wyloc = self.wrap_calc_x(xloc+i), self.wrap_calc_y(yloc+j)
                array[i].append(self.landscape[wxloc][wyloc])
        return array

