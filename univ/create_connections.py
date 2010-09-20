import random
import sys

my_file = open('connex','w')
#layer_sizes = [[3,3,1],[3,3,2],[3,3,2],[3,3,1],[3,1,1]]
layer_sizes = [[7,7,1],[7,7,2],[3,3,1],[3,1,1]]
#layer_sizes = [[3,3,1],[3,3,2],[3,3,1],[3,1,1]]

#synsumco = [0.06, 0.431, 0.445 ]
synsumco = [0.06, 0.431]
num_layers = len(layer_sizes)

#write layer_sizes to file
my_file.write(str(len(layer_sizes)))
for layer in layer_sizes:
    my_file.write('\n')
    for elm in layer:
        my_file.write(str(elm)+ ' ')
my_file.write('\n')


#write synsumco to file
for syn_sum in synsumco:
   my_file.write(str(syn_sum) + ' ' )
my_file.write('\n')

cell_type_ext = 0
cell_type_in = 1

x_out = 0.015
in_top = 0.15

total_x_out =0.0
x_out_num = 0


#basic way of connecting layer to layer
def connect_layers(pre_layer,post_layer,pre_type,post_type,one_to_one,fast,plastic,stren):

    fast = str(int(fast))
    plastic = str(int(plastic))
    total_strength = 0.0
    num_connections = 0

    for y in range(layer_sizes[pre_layer][0]):
        for x in range(layer_sizes[pre_layer][1]):
            if one_to_one:
                my_file.write(str(pre_type)+' '+str(pre_layer)+' '+str(y)+' ' + str(x) +' ' + str(post_type)+' '+str(post_layer) + ' '+str(y)+' ' + str(x) + ' ' + str(stren) + ' ' + fast + ' ' + plastic + '\n')
                total_strength = total_strength + stren
                num_connections = num_connections + 1
            else:
                for y_post in range(layer_sizes[post_layer][0]):
                    for x_post in range(layer_sizes[post_layer][1]):
                        my_file.write(str(pre_type)+' '+str(pre_layer)+' '+str(y)+' ' + str(x) +' ' + str(post_type)+' '+str(post_layer) + ' '+str(y_post)+' ' + str(x_post) + ' ' + str(stren) + ' ' + fast + ' ' + plastic + '\n')
                        total_strength = total_strength + stren
                        num_connections = num_connections + 1

    return total_strength, num_connections

#new setup
#input to top
#connect_layers(0,1,cell_type_ext,cell_type_ext,True,True,True,in_top)
#connect_layers(0,1,cell_type_ext,cell_type_in,True,True,True,in_top)

#top to top inhibition
#connect_layers(1,1,cell_type_in,cell_type_ext,False,True,True,-in_top)

#top to bottum
#tstren,nconnect=connect_layers(1,2,cell_type_ext,cell_type_ext,False,True,True,in_top)
#connect_layers(1,2,cell_type_ext,cell_type_in,False,True,True,in_top)
#connect_layers(1,2,cell_type_in,cell_type_ext,False,True,True,-(tstren/nconnect))
#connect_layers(1,2,cell_type_in,cell_type_in,False,True,True,-(tstren/nconnect))

#bottum to output
#tstren,nconnect = connect_layers(2,3,cell_type_ext,cell_type_ext,False,True,True,x_out)
#print -tstren/nconnect,'in to out s', nconnect,'num ext to out', tstren,'total ext to out strength'
#connect_layers(2,3,cell_type_in,cell_type_ext,False,True,True,-(tstren/nconnect))


#old setup
#input to top
connect_layers(0,1,cell_type_ext,cell_type_ext,True,True,True,in_top)
connect_layers(0,1,cell_type_ext,cell_type_in,True,True,True,in_top)
        
#top to output
tstren,nconnect = connect_layers(1,2,cell_type_ext,cell_type_ext,False,True,True,x_out)
connect_layers(1,2,cell_type_in,cell_type_ext,False,True,True,-tstren/nconnect)
        

#specific set ups for special connectivity
for z in range(num_layers):
    for y in range(layer_sizes[z][0]):
        for x in range(layer_sizes[z][1]):

            #this is emotion layer: reward and punish connect to hunger, hunger connects to all to inhibit
            if z==num_layers-1:

                #reward to hunger
                if y ==0:
                    my_file.write(str(cell_type_ext)+' '+str(z)+' '+str(y)+' ' + str(x) +' ' + str(cell_type_ext)+' '+str(z) + ' '+str(2)+' ' + str(x)+' '+ str(-.1)+' 0' + ' 0' +'\n')

                #punish to hunger
                if y == 1:
                    my_file.write(str(cell_type_ext)+' '+str(z)+' '+str(y)+' ' + str(x) +' ' + str(cell_type_ext)+' '+str(z) + ' '+str(2)+' ' + str(x)+' '+ str(0.0025)+' 0' + ' 0' + '\n')

                #hunger to others
                if y == 2:
                    for yi in range(layer_sizes[1][0]):
                        for xi in range(layer_sizes[1][1]):
                            print 'create inhibition'
                            my_file.write(str(cell_type_ext)+' '+str(z)+' '+str(y)+' ' + str(x) +' ' + str(cell_type_ext)+' '+str(1) + ' '+str(yi)+' ' + str(xi)+' '+ str(-0.0015)+' 0' + ' 0' +'\n')
                            my_file.write(str(cell_type_ext)+' '+str(z)+' '+str(y)+' ' + str(x) +' ' + str(cell_type_in)+' '+str(1) + ' '+str(yi)+' ' + str(xi)+' '+ str(-0.0015)+' 0' + ' 0' +'\n')


                












