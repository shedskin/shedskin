import math
import random
#import pylab

class SynEvent:
    
    def reset(self):
        self.synapse= 0.0

    def __init__(self,slow):
        self.reset()
        self.slow = slow

    def calc_event(self,ctime,parent_cell):
        if self.slow:
            self.synapse = self.synapse * 0.99995#?97 TODO
            if ((math.fabs(self.synapse) < 0.00001) and (self.synapse != 0.0)):
                self.reset()
        else:
            self.synapse = self.synapse * 0.99#0.99#?97 TODO
            if ((math.fabs(self.synapse) < 0.00001) and (self.synapse != 0.0)):
                self.reset()

class Connection:

    def __init__(self,post_cell,pre_cell,s,fast,plastic):
        self.post_cell = post_cell # post cell
        self.pre_cell = pre_cell
        self.s = s
        self.plas_trace = []
        self.fast = fast
        self.plastic = plastic

class Cell:

    al = 3.65 #map stretch
    sig = 0.06 #baseline input
    mu = 0.0005 #scales change of u
    beta_e = 0.133 #scales input

    def __init__(self,index,total_time,layer,x,y,cell_type,lmax,brain):
        self.brain = brain
        self.syndeviance = .075
        self.fire_time = -10000 # problem with twice firing
        self.lmax = lmax

        if layer == lmax-1:
            self.dc = 0.013
        elif layer == 0 or layer == lmax -2:
            self.dc = 0.033#0.013
        else:
            self.dc= -0.0165

        #if layer == lmax-2 and x==0 and y==0:
            #print 'set high dc cell'
            #self.dc = 0.1

        self.last_fire = 0
        self.fat = 0.5
        self.cell_type = cell_type
        self.index = index 
        self.syn_event_fast = SynEvent(False)
        self.syn_event_slow = SynEvent(True)
        self.reset()
        self.syn_sym = 0
        self.coef = 0.2
        self.connections = []
        self.in_coming = []
        self.mem = (0.0,0.0,0.0)
        self.layer = layer
        self.input = 0.0
        self.x = x
        self.y = y
        self.trans_level = 0 

    def reset(self):
        self.network = -0.927 #depolarization (starting state)
        self.fired=0 #cells firing this iteration
        self.input= 0.0
        self.umm = -2.822286
        self.u = -2.821135
        self.cond1=False
        self.cond2=False
        self.cond3=False
        self.cond4=False

    def calc_next_state(self,ctime):
        self.cond1=False
        self.cond2=False
        self.cond3=False
        self.cond4=False

            #this block takes the current state of the cell and transforms it to the next state
        self.umm =self.umm - Cell.mu*(self.network+1)+(Cell.mu*Cell.sig)+Cell.mu*self.input
        self.u= self.umm+(Cell.beta_e*self.input)
        
        if self.network <= 0: #cond 1
            self.cond1 = True
        if (self.network > 0) and (self.network < Cell.al+self.u) and (self.mem[2] <=0): #cond2
            self.cond2 = True

        if (self.network >= (Cell.al +self.u)) or (self.mem[2]>0): #cond3
            self.cond3 = True

        if (self.network >0) and (self.network < Cell.al + self.u) and (self.mem[2] <=0): #cond2a
            self.cond4 = True

        if self.cond1:
            self.network = Cell.al/(1-self.network) + self.u
            if self.layer==3 and self.x==2 and ctime%10==0:
                pass
                #print ctime,' ', self.network
        if self.cond2:
            self.network = Cell.al +self.u
        if self.cond3:
            self.network = -1.0
           

        
        self.mem = (self.network,self.mem[0],self.mem[1])

        if self.cond4: 
            self.trans_level = self.trans_level * self.fat
            self.fired =1
            self.last_fire = ctime
        else:
            self.trans_level = (self.trans_level * 0.95) + 0.05
            self.fired = 0

        if random.random() < self.brain.noise_rate and ((self.layer+2) != self.lmax) and ((self.layer+1) != self.lmax):
            self.syn_event_fast.synapse = self.syn_event_fast.synapse + random.random()*self.brain.noise

        self.input = self.dc

        self.syn_event_fast.calc_event(ctime,self)
        self.syn_event_slow.calc_event(ctime,self)

        #if ctime == events[0] + window or ctime == events[2]+window or ctime == events[3]+window or ctime == events[4]+window:
        #    if self.layer == 1:
        #        self.syn_event.reset()
        #        self.reset()

        
        self.input = self.input + self.syn_event_fast.synapse +self.syn_event_slow.synapse


    #this modifies incoming connections
    def balance_connections(self,synsumco):
        
        if len(self.in_coming) < 1:
            return

        connex_sum = 0.0

        #first we find out the total strength of positive plastic incoming connections
        for connection in self.in_coming:
            if connection.s > 0 and connection.plastic:
                connex_sum = connex_sum + connection.s

  
        scaler = synsumco[self.layer-1] / connex_sum
 

        connex_sum = 0.0
        connex_total = 0
        #then we rescale positive placitic incoming connections so that they sum to synsum co
        for connection in self.in_coming:
            if connection.s > 0 and connection.plastic:
                connection.s = connection.s * scaler
                connex_sum = connex_sum + connection.s
                connex_total = connex_total + 1

        #if my layer is 2 and i am inhibitory make my positive incoming connections match the positive connections to the exite cells in the same layer
        if self.layer == 2 and self.cell_type == 1:
            k = 0
            for connection in self.brain.cell_array[2][self.x][self.y][0].in_coming:
                #print 'for loop'
                if connection.s > 0:
                    while True:
                        #print k,'while loop'
                        if self.in_coming[k].s > 0:
                            #print 'positive'
                            self.in_coming[k].s = connection.s
                            break
                        k = k + 1

        #if self.layer == 1 and self.cell_type == 1:
            #for connection in self.in_coming:
                #connection.s = connection.s * 2

        #make my incoming negative connection strengts uniform and sum to equal my sum of incoming positve connections
        for connection in self.in_coming:
            if connection.s < 0 and connection.plastic and connection.pre_cell.layer + 1 == self.layer:
                connection.s = -(connex_sum / connex_total)
                        
        return
        
    #thank you scholarpedia http://www.scholarpedia.org/article/Spike-timing_dependent_synaptic_plasticity#Basic_STDP_Model
    def stdp(self,pre_time,post_time,c_strength): #returns change to connection strength
        #print 'stdp event'
        #print 'pre_time' ,pre_time
        #print 'post_time' ,post_time
        #print 'c_strength' ,c_strength

        

        tau = 20.0
        if pre_time > post_time:
            sscale = -0.025
        else:
            #sscale = 0.05
            sscale = 0.025
            

        x = abs(pre_time - post_time)

        if x > 400:
            #print 'delta 0'
            return 0.0

        if x != 0:
            delta = sscale*c_strength*math.exp(-x/tau)
            if delta > 0.1:
                return 0.1
            #print 'delta' ,delta
            return delta
        if x == 0:
            #print 'delta 0 2'
            return 0.0




    def apply_fire(self,ctime):
        self.fire_time = ctime

        if random.random() > 0.01 or len(self.connections) <= 2:
            syn_random= False
        else:
            syn_random = True
            syn_fail,syn_double=random.sample(range(len(self.connections)),2)

        i = -1
        for connection in self.connections:#branch failure is off
            i = i + 1
            #currently does nothing
            if self.layer==0:
                #print self.brain.inscale
                layscale=self.brain.inscale
                layscale=1.0
            else:
                layscale=1.0

            #TODO might need to change this if we need different time constaplasticnts
            
            if syn_random and i == syn_fail:
                continue
            elif syn_random and i == syn_double:
                if connection.fast:
                    connection.post_cell.syn_event_fast.synapse = connection.post_cell.syn_event_fast.synapse + (connection.s * self.trans_level*(random.normalvariate(1,self.syndeviance)))*layscale*2
                else:
                    connection.post_cell.syn_event_slow.synapse = connection.post_cell.syn_event_slow.synapse + (connection.s * self.trans_level*(random.normalvariate(1,self.syndeviance)))*layscale*2
            else:
                if connection.fast:
                    connection.post_cell.syn_event_fast.synapse = connection.post_cell.syn_event_fast.synapse + (connection.s * self.trans_level*(random.normalvariate(1,self.syndeviance)))*layscale
                else:

                    connection.post_cell.syn_event_slow.synapse = connection.post_cell.syn_event_slow.synapse + (connection.s * self.trans_level*(random.normalvariate(1,self.syndeviance)))*layscale

            delta_s = self.stdp(self.fire_time,connection.post_cell.fire_time,connection.s)
            if connection.plastic and connection.s > 0:
                if  self.brain.reward_on:
                    connection.plas_trace.append( (ctime,delta_s))
                else:
                    connection.s = connection.s + delta_s

            connection.last_fire = ctime

        for connection in self.in_coming:            
            if connection.s > 0 and connection.plastic:
                delta_s = self.stdp(connection.pre_cell.fire_time,self.fire_time,connection.s)

                if  self.brain.reward_on:
                    connection.plas_trace.append( (ctime,delta_s))
                else:
                    connection.s = connection.s + delta_s

        new_connections = []
        for i in range(len(self.connections)):

            # if connection is too small to remain
            if self.connections[i].post_cell.cell_type == 0 and self.connections[i].pre_cell.cell_type ==0 and self.connections[i].s < 0.001 and self.connections[i].pre_cell.layer < self.lmax - 2 and self.connections[i].plastic and False:
                print 'creating self.connections[i] old_strength: ' + str(self.connections[i].s)
                post_layer = self.connections[i].post_cell.layer
                post_type = self.connections[i].post_cell.cell_type
                
                #find out who new to connect to
                while True:
                    post_x = random.randint(0,self.brain.layer_sizes[post_layer][0]-1)
                    post_y = random.randint(0,self.brain.layer_sizes[post_layer][1]-1)
                    post_cell = self.brain.cell_array[post_layer][post_x][post_y][post_type]

                    already_connected = False
                    for connect in self.connections:
                        if connect.post_cell.x == post_x and connect.post_cell.y == post_y:
                            already_connected = True

                    if not already_connected or (post_x == self.connections[i].post_cell.x and post_y == self.connections[i].post_cell.y):
                            break

                
                connex_sum = 0.0
                connex_total = 0
                for connect2 in self.in_coming:
                    if connect2.s > 0:
                        connex_sum = connex_sum + connect2.s
                        connex_total = connex_total + 1

                if connex_total >1:
                    new_s = (connex_sum / (connex_total-1))
                else:
                    new_s = (connex_sum / (connex_total))

                #creates the new connection and destroys the old
                self.connections[i].post_cell.in_coming.remove(self.connections[i])
                new_connection = Connection(post_cell,self,new_s,True,True)
                new_connections.append(new_connection)
                post_cell.in_coming.append(new_connection)
            else:
                pass
                new_connections.append(self.connections[i])

        self.connections = new_connections

class Brain:

    def __init__(self,lmax,layer_sizes,ttime,average_syn_file,reward_on,connex,base_noise,base_noise_rate):
        self.connex = connex
        self.average_syn_file = average_syn_file
        self.layer_sizes = layer_sizes
        self.lmax = lmax
        self.ttime = ttime
        self.flash_strength = 0.03
        self.cell_array = self.create_cells(lmax,layer_sizes,ttime)
        self.connect_cells(self.cell_array,self.connex)
        self.done = False
        self.savg = []
        self.reward_on = reward_on
        self.inscale=1
        self.noise = base_noise#amplitude
        self.noise_rate = base_noise_rate
    
    def create_cells(self,lmax,layer_sizes,ttime):
        total = 0
        cell_array = []
        for i in range(lmax):
            cell_array.append([])
            for j in range(layer_sizes[i][0]):
                cell_array[i].append([])
                for k in range(layer_sizes[i][1]):
                    cell_array[i][j].append([])
                    for l in range(layer_sizes[i][2]):
                        cell_array[i][j][k].append(Cell(total,ttime,i,j,k,l,lmax,self))
    
        return cell_array
        
    def connect_cells(self,cells,connex):
        for line in connex:
            coxdat=line.split()
            cell_type1,x,y,z,cell_type2,i,j,k,s,fast,plastic=coxdat[0],coxdat[1],coxdat[2],coxdat[3],coxdat[4],coxdat[5],coxdat[6],coxdat[7],coxdat[8],coxdat[9],coxdat[10]
            #print 'cell_type1 x y z i j k cell_type2',cell_type1,x,y,z,i,j,k,cell_type2
            #print len(cells),len(cells[int(x)]),len(cells[int(x)][int(y)]),len(cells[int(x)][int(y)][int(z)])
            #print  len(cells),len(cells[int(i)]),len(cells[int(i)][int(j)]),len(cells[int(i)][int(j)][int(k)])
            cells[int(x)][int(y)][int(z)][int(cell_type1)].connections.append(Connection(cells[int(i)][int(j)][int(k)][int(cell_type2)],cells[int(x)][int(y)][int(z)][int(cell_type1)],float(s),bool(int(fast)), bool(int(plastic))))

        for layer in self.cell_array:
            for row in layer:
                for item in row:
                    for cell in item:
                        for connection in cell.connections:
                            connection.post_cell.in_coming.append(connection)

    def apply_inputs(self,grid):
        for i,row in enumerate(grid):
            for j,item in enumerate(row):
                if item == 1 or item == 3 or item==4:
                    self.cell_array[0][i][j][0].dc = self.cell_array[0][i][j][0].dc + 0.05
        return grid

    def unflash(self,grid):
        for i,row in enumerate(grid):
            for j,item in enumerate(row):
                if item == 1 or item == 3 or item==4:
                    self.cell_array[0][i][j][0].dc = self.cell_array[0][i][j][0].dc - 0.05

    def reward(self,food):
        #one day we would like to use a synapse for input
        #this flashes the reward cell
        if food:
            self.cell_array[self.lmax-1][0][0][0].syn_event_fast.synapse = self.flash_strength
            pass
        else:
            self.cell_array[self.lmax-1][1][0][0].syn_event_fast.synapse = self.flash_strength
            pass
             
    def calc(self,ctime):
        total = 0
        i = 0
        for layer in self.cell_array:
            for row in layer:
                for item in row:
                    for cell in item:
                        cell.calc_next_state(ctime)
                        if ctime%1000==0:
                            for connection in cell.connections:
                                if connection.pre_cell.cell_type == 0 and connection.post_cell.cell_type==0 and connection.post_cell.layer != self.lmax -2 and connection.post_cell.layer != self.lmax -3:
                                    total = connection.s + total
                                    i = i +1

        #if ctime%1000==0 and self.lmax > 3:
            #self.average_syn_file.write(str(total/i) + '\n')

        #self.savg.append(total/i)
        #if ctime > 10000:
        #    pylab.plot(self.savg)
        #    pylab.show()
        #    exit(1)


    def calc_reward_scale(self,cell):
        sum_out_connections = 0.0
        num_in_next = 0.0
        s_in_next = 0.0

        
        num_plastic = 0.0
        neg_c = False
        for plas_check_con in cell.connections:
            if plas_check_con.s < 0:
                neg_c = True
            if plas_check_con.plastic:
                num_plastic = num_plastic + 1.0        

        if len(cell.connections) < 1 or num_plastic < 1 or neg_c:
            return 0.0

        for out_connect in cell.connections:
            if out_connect.s > 0:
                sum_out_connections = sum_out_connections + out_connect.s

        for row in self.cell_array[cell.layer+1]:
            for item in row:
                for cell_looped in item:
                    for connection in cell_looped.in_coming:
                        if connection.s > 0:
                            s_in_next = s_in_next + connection.s
                            num_in_next = num_in_next + 1.0

        reward_scale = (s_in_next*len(cell.connections))/(num_in_next*sum_out_connections)
        return reward_scale

    def fire(self,ctime,epoch,spikes_per_e,happyness,happyfile,choices):
        fired = 0
        outx = 0
        outy = 0
        reset_trace = False
        #go through all cells except eward cell
        for z,layer in enumerate(self.cell_array[:-1]):
            for y,row in enumerate(layer):
                for x,element in enumerate(row):
                    for w,cell in enumerate(element):


                        if cell.fired > 0:
                            #accounting information number of spikes per layer per epoch
                            spikes_per_e[z]=spikes_per_e[z]+1
                            #if it is a cell in the output layer report that an output layer cell has fired
                            if z == self.lmax-2:
                                outx, outy = y,x #god knows why this is like this
                                choices[x][y] = 1
                                fired = fired +1
                            #print 'layer z x y fired ',cell.layer,z,cell.x,cell.y
                            cell.apply_fire(ctime)
                            cell.fired = 0



        if self.cell_array[self.lmax-1][0][0][0].fired:
            self.cell_array[self.lmax-1][0][0][0].apply_fire(ctime)
            happyness=happyness*.9999+.0001
            happyfile.write(str(happyness)+' '+str(ctime)+'\n')

        if self.cell_array[self.lmax-1][1][0][0].fired:
            self.cell_array[self.lmax-1][1][0][0].apply_fire(ctime)
            happyness=happyness*.9999
            happyfile.write(str(happyness)+' '+str(ctime)+'\n')

        if self.cell_array[self.lmax-1][2][0][0].fired:
            self.cell_array[self.lmax-1][2][0][0].apply_fire(ctime)


        #if reward cell fires
        if self.cell_array[self.lmax-1][0][0][0].fired or self.cell_array[self.lmax-1][1][0][0].fired:

            #go through all connections in network and apply stdp
            for layer in self.cell_array:
                for row in layer:
                    for item in row:
                        for cell in item:
                            reward_scale = self.calc_reward_scale(cell)
                            #print reward_scale,'reward scale'
                            #print 'layer',cell.layer
                            #print 'x y', cell.x,cell.y
                            #print 'type',cell.cell_type
                            for connection in cell.connections:
                                new_traces = []
                                for i,trace in enumerate(connection.plas_trace):
                        
                                    if ctime - trace[0] < 3*epoch and connection.plastic:
                                        if self.cell_array[self.lmax-1][0][0][0].fired:
                                            old_s = 0.0
                                            old_s = connection.s
                                            connection.s = connection.s + (trace[1]/(1+((ctime-trace[0])/epoch))) * reward_scale
                                            if connection.s < 0.5 * old_s:
                                                connection.s = 0.5 * old_s

                                        elif self.cell_array[self.lmax-1][1][0][0].fired:
                                            connection.s = connection.s - (trace[1]/(1+((ctime-trace[0])/epoch)))*.4

                                        new_traces.append(trace)
                                connection.plas_trace = new_traces

                            

        self.cell_array[self.lmax-1][0][0][0].fired = 0 
        self.cell_array[self.lmax-1][1][0][0].fired = 0  
        self.cell_array[self.lmax-1][2][0][0].fired = 0  
                  
        return [outx,outy,fired,happyness]


