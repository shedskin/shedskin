import time, math, random, os, sys
import pygame
import spirit, enviroment

movie = True

def record(ctime, layer_sizes, spirit_brain):
    points_file=open(folder_name+'/points'+(str(ctime/1000000)),'w')
    points_file.write('points: '+ str(points) +' rewarded: ' + str(reward))
    connex_final_file=open(folder_name+'/connex'+(str(ctime/1000000)),'w')
    food_file=open(folder_name+'/burger_time','w')
    out_spike_file=open(folder_name+'/out_spike','w')
    
    if total_wrong_food > 0:
        food_type_file.write(str(float(total_food)/float(total_wrong_food))+ '\n')
    

    connex_final_file.write(str(lmax)+'\n')
    for layer_size in layer_sizes:
        connex_final_file.write(str(layer_size[0]) +' ' + str(layer_size[1]) + ' '+ str(layer_size[2]) + '\n')

    for syn_sum in synsumco:
        connex_final_file.write(str(syn_sum) + ' ' )
    connex_final_file.write('\n')

    for layer in spirit_brain.cell_array:
        for row in layer:
            for item in row:
                for cell in item:
                    for connection in cell.connections:
                        other_cell = connection.post_cell
                        connex_final_file.write( str(cell.cell_type)  + ' ' + str(cell.layer) + ' ' +  str(cell.x) + ' ' +  str(cell.y) + ' ' + str(other_cell.cell_type) + ' ' +str(other_cell.layer)  + ' ' +  str(other_cell.x) + ' ' +  str(other_cell.y) + ' ' +   str(connection.s) + ' ' + str(int(connection.fast))+ ' ' + str(int(connection.plastic)) +'\n')

    food_times.append(ctime)
    for food_time in food_times:
        food_file.write(str(food_time) +'\n')

    out_spikes.append(ctime)
    for out_spike in out_spikes:
        out_spike_file.write(str(out_spike) +'\n')

    points_file.close()
    connex_final_file.close()
    food_file.close()
    out_spike_file.close()

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

def determine_heading(max_index):
    if len(max_index) > 0:
        x,y = random.choice(max_index);
        if x==0 and y==0:
            heading = 'north_west'
        if x==0 and y==1:
            heading = 'west'
        if x==0 and y==2:
            heading = 'south_west'
        if x==1 and y==0:
            heading='north'
        if x==1 and y==1:
            heading='north'#could be null but that tends to mess things up
        if x==1 and y==2:
            heading='south'
        if x==2 and y==0:
            heading='north_east'
        if x==2 and y==1:
            heading='east'
        if x==2 and y==2:
            heading='south_east'

        #print heading
    else:
        if random.random() > 0.98:
            x = random.randint(0,1)
            if x==0 and heading == 'north':
                heading = 'north_east'
            elif x==1 and heading == 'north':
                heading = 'north_west'

            elif x==0 and heading == 'south':
                heading = 'south_east'
            elif x==1 and heading == 'south':
                heading = 'south_west'

            elif x==0 and heading== 'east':
                    heading = 'north_east'
            elif x==1 and heading== 'east':
                heading='south_east'

            elif x==0 and heading== 'west':
                    heading = 'north_west'
            elif x==1 and heading== 'west':
                heading='south_west'

            elif x==0 and heading== 'north_west':
                    heading = 'west'
            elif x==1 and heading== 'north_west':
                heading='north'

            elif x==0 and heading== 'north_east':
                    heading = 'east'
            elif x==1 and heading== 'north_east':
                heading='east'

            elif x==0 and heading== 'south_east':
                    heading = 'east'
            elif x==1 and heading== 'south_east':
                heading='south'

            elif x==0 and heading== 'south_west':
                heading = 'south'
            elif x==1 and heading== 'south_west':
                heading='west'

            elif x==0 and heading== 'null':
                heading = 'north'
            elif x==1 and heading== 'null':
                heading='south'

    return heading

def main():
    if movie:
        pygame.init()

    univ = Universe()
    if movie:
        display = Display(univ)

    for ctime in range(2,univ.ttime):
        univ.advance(ctime)
        if movie and ctime%100 == 0:
            display.update(ctime)
        if ctime%10000 == 0:
            print('time: ' + str(ctime) + ' happy: ' + str(univ.happyness))

    record(univ.ttime, univ.layer_sizes, univ.spirit_brain)
    print('finish calc')

class Display:
    def __init__(self, univ):
        self.univ = univ
        self.window = pygame.display.set_mode((1200, 1200)) 
        self.screen = pygame.display.get_surface() 

    def update(self, ctime):
        univ = self.univ
        my_env = univ.my_env
        update_rects = []
        for i in range(my_env.xsize):
             for j in range(my_env.ysize):
                 obj = my_env.landscape[i][j]
                 rect = my_env.rects[i][j]
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
        
class Universe:
    def __init__(self):
        self.parse_options()
        self.folder_name = self.get_folder_name()

        self.epoch = 800
        self.start_width = 600
        self.points= 0
        self.env_size = 100
        self.my_env = enviroment.Enviroment(self.env_size,self.env_size,self.env_size**2/10,movie,self.food_type,"homo")
        self.sleeper=False
        self.reward_hold=self.reward
        self.wake=True
        self.up_time=400000
        self.down_time=400
        self.alert=self.up_time
        self.cyclet=50
        self.base_noise_rate = 0.000
        self.base_noise = 0.00
        self.msouth = True
        self.out_per_f=0
        self.happyness=0.1
        self.cycle=self.cyclet
        self.sleep_noise_level = 0.05

        self.cell_array = []
        self.connex_file=open('connex','r')
        self.layer_sizes=[]
        self.lmax=int(self.connex_file.readline()) #number of layers
        self.spikes_per_e=[0]*self.lmax
        self.totalstuff=[0]*self.lmax
        for i in range(self.lmax):
            self.layer_sizes.append([])
            for char in self.connex_file.readline().split():
                self.layer_sizes[i].append(int(char))

        self.synsumco = []
        self.syn_line = self.connex_file.readline()
        for syn in self.syn_line.split():
            self.synsumco.append(float(syn))
        #synsumco = [0.153,.153,1.95]

        self.average_syn_file = open(self.folder_name+'/average_syn','w')
        if self.control_cond:
            self.control_file = open(self.folder_name+'/control','w')
        self.average_syn_file = open(self.folder_name+'/average_syn','w')
        #food_file = open(folder_name+'/burger_time','w')
        #connex_final_file = open(folder_name + '/connex_final','w')
        #points_file = open(folder_name + '/points','w')
        self.layertotals_file=open(self.folder_name + '/layertotals','w')
        self.happyfile=open(self.folder_name + '/happyfile','w')
        self.food_type_file= open(self.folder_name + '/food_types','w')
        self.total_food = 0
        self.total_wrong_food = 0



        self.spirit_brain = spirit.Brain(self.lmax,self.layer_sizes,self.ttime,self.average_syn_file,self.reward,self.connex_file,self.base_noise,self.base_noise_rate)
        self.last='north'

        print('start calc')
        self.still = 0
        self.fired_yet = False
        self.yum = 0
        self.dir_time = 0
        self.flash_on  = True
        self.heading = 'north'
        self.food_times = []  
        self.out_spikes = []         
        self.food_all = []
        self.fire_now =False
        self.choices = [[0,0,0],[0,0,0],[0,0,0]] 
        self.spike_counter = [[0,0,0],[0,0,0],[0,0,0]]
        self.flash_grid = []

    def advance(self, ctime):
        spirit_brain = self.spirit_brain
        spikes_per_e = self.spikes_per_e
        my_env = self.my_env

        spirit_brain.calc(ctime)

        if ctime%self.epoch==0:

            if spikes_per_e[0]>0:
                #top to bottum
                #if spikes_per_e[1]>spikes_per_e[2]:
                    #synsumco[1]=synsumco[1]*1.001
                #if spikes_per_e[1]<spikes_per_e[2]:
                    #synsumco[1]=synsumco[1]*.999

                #bottum to output

                if spikes_per_e[1] > spikes_per_e[0]:
                    for row in spirit_brain.cell_array[1]:
                        for item in row:
                            for cell in item:
                                cell.dc = cell.dc - .0001

                    print spirit_brain.cell_array[1][0][0][0].dc,'down'

                if spikes_per_e[1] < spikes_per_e[0]:
                    for row in spirit_brain.cell_array[1]:
                        for item in row:
                            for cell in item:
                                cell.dc = cell.dc + 0.0001
                    print spirit_brain.cell_array[1][0][0][0].dc,'up'


                #print out_per_f
                #if out_per_f > 1:
                #    out_spikes.append(ctime)
                #if out_per_f>1:
                #    synsumco[1]=synsumco[1]*.999 #for a 5 total 
                #if out_per_f==0:
                #    synsumco[1]=synsumco[1]*1.001

            self.choices = [[0,0,0],[0,0,0],[0,0,0]]


            if spirit_brain.noise_rate < self.base_noise_rate * 10:
                spirit_brain.noise_rate = spirit_brain.noise_rate * 1.1
                spirit_brain.noise = spirit_brain.noise * 1.05

            for layer in spirit_brain.cell_array[1:len(spirit_brain.cell_array)-1]:
                for row in layer:
                    for item in row:
                        for cell in item:
                            cell.balance_connections(self.synsumco)

            for i,layer_print in enumerate(self.totalstuff[:-1]):
                self.totalstuff[i] = layer_print + spikes_per_e[i] 
            self.totalstuff[-1] = self.points

            self.out_per_f=0
            spikes_per_e=[0]*self.lmax
            
            for i,layer_print in enumerate(self.totalstuff):
                self.layertotals_file.write(str(layer_print) + ' ' )
            self.layertotals_file.write('\n')
     
        #half way through epoch
        if (ctime+self.epoch/2)%self.epoch==0 and self.wake:
            spirit_brain.unflash(self.flash_grid)
            self.visionsum=0

            max_index = []
            maximum = -1
            for i,line in enumerate(self.spike_counter):
                for j,out_cell_spikes in enumerate(line):
                    if out_cell_spikes > maximum:
                        maximum = out_cell_spikes
                        max_index = [[i,j]]
                    if out_cell_spikes == maximum:
                        max_index.append([i,j])

            self.spike_counter = [[0,0,0],[0,0,0],[0,0,0]]

            self.heading = determine_heading(max_index)
                
            self.food_type = my_env.move_crit(self.heading)
            if self.food_type == "bacon": 
                self.total_food = self.total_food + 1
                self.food = True
            if self.food_type== "grass":
                self.total_wrong_food = self.total_wrong_food + 1
                self.food = False
            if self.food_type== "blank":
                self.food = False

            spirit_brain.reward(self.food)
            if self.food:
                self.food = False
                self.food_times.append(ctime)
            
        # start of epock get vision
        if ctime%self.epoch==0:

            self.vision = my_env.get_vision(my_env.critx,my_env.crity,(self.layer_sizes[0][0]-1)/2,(self.layer_sizes[0][1]-1)/2)
            for vision_row in self.vision:
                for vis_cell in vision_row:
                    if vis_cell==1:
                        self.visionsum=self.visionsum+1

            if self.visionsum==0:
                self.visionsum=1

            spirit_brain.inscale=1.0/float(self.visionsum)
            self.flash_grid = spirit_brain.apply_inputs(self.vision)


        self.array = []
        self.array=spirit_brain.fire(ctime,self.epoch,spikes_per_e,self.happyness,self.happyfile,self.choices)
        self.out_per_f=sum(self.choices[0])+sum(self.choices[1]) + sum(self.choices[2])
        self.happyness = self.array[3]
        for m in range(3):
            for n in range(3):
                self.spike_counter[m][n] = self.spike_counter[m][n] + self.choices[m][n]

        if ctime%1000000==0:
            record(ctime, self.layer_sizes, spirit_brain)

    def get_folder_name(self):
        count = 1
        while True:
            if not os.access('output/'+str(count),os.F_OK):
                os.mkdir('output/'+str(count))
                os.popen('cp connex output/' + str(count))
                folder_name = 'output/'+str(count)
                break
            print count
            count = count + 1
        return folder_name

    def parse_options(self):
        if len(sys.argv) != 5:
            print 'bad ars need reward[True|False] run_time[int] control[True|False] food_type[horz|vert]'
            
            self.reward = True
            self.control_cond = False
            self.ttime=10000000 # number of iterations
            self.food_type = "vert"
        else:
            self.ttime=int(sys.argv[2]) # number of iterations
            if sys.argv[1] == 'False':
                self.reward = False
            elif sys.argv[1] == 'True':
                self.reward = True
            else:
                print 'bad ars need reward[True|False] run_time[int] control[True|False] food_type[horz|vert]'
                exit(1)

            if sys.argv[3] == 'False':
                self.control_cond = False
            elif sys.argv[3] == 'True':
                self.control_cond = True
            else:
                print 'bad ars need reward[True|False] run_time[int] control[True|False] food_type[horz|vert]'
                exit(1)

            if sys.argv[4] == 'vert':
                self.food_type = 'vert'
            elif sys.argv[4] == 'horz':
                self.food_type = 'horz'
            else:
                print 'bad ars need reward[True|False] run_time[int] control[True|False] food_type[horz|vert]'
                exit(1)


if __name__ == '__main__':
    main()
