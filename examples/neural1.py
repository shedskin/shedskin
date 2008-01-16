# (c) Mark Dufour
# --- mark.dufour@gmail.com
#
# back-propagation neural network 

from random import random
from math import sqrt, e

sigmoid = lambda x: pow((1+pow(e,-x)),-1) # [lambda0]
deriv = lambda x: pow(e,-x) * pow((1+pow(e,-x)),-2) # [lambda0]

class link:                             # in_node: [node], weight: [float], activation: [], out_node: [node], delta: [], input: [], output: [], unit: []
    def __init__(self, in_node, out_node): # self: [nlink], in_node: [node]*, out_node: [node]*
        self.in_node = in_node; self.out_node = out_node # [node]
        self.weight = (random()-0.5)/2  # [float]
        
class node:                              # in_node: [], weight: [], activation: [float], out_node: [], delta: [float], output: [list(nlink)], input: [list(nlink)], unit: []
    def __init__(self, input_nodes):     # self: [node], input_nodes: [list(node)]
    	self.input, self.output = [], []    # [list(nlink)], [list(nlink)]
        for node in input_nodes:         # [list(node)]
            l = link(node,self)         # [nlink]
            self.input.append(l)         # []
            node.output.append(l)        # []

def incoming(node): return sum([link.in_node.activation * link.weight for link in node.input]) # [float]

def neural_network_output(network, input): # network: [list(list(node))], input: [list(int)]
    # set input layer activations
    for index, node in enumerate(network[0]): # [tuple(int, node)]
        node.activation = input[index]   # [int]
        
    # forward propagate output 
    for layer in network[1:]:            # [list(list(node))]
        for node in layer:               # [list(node)]
            node.activation = sigmoid(incoming(node)) # [float]

    return [node.activation for node in network[-1]] # [list(float)]

def back_propagate_error(network, answer): # network: [list(list(node))], answer: [list(int)]
    #output = [node.activation for node in network[-1]] # [list(float)]

    # output layer deltas
    for index, node in enumerate(network[-1]): # [tuple(int, node)]
        node.delta = deriv(incoming(node)) * (answer[index] - node.activation) # [float]

    # backward propagate error
    for layer in network[-2::-1]:        # [list(list(node))]
        for node in layer:               # [list(node)]
            node.delta = deriv(incoming(node)) * sum([link.out_node.delta * link.weight for link in node.output]) # [float]
            for link in node.output:     # [list(nlink)]
                link.weight += alpha * node.activation * link.out_node.delta # [float]
	         
def append_error(network, examples):     # network: [list(list(node))], examples: [list(tuple(list(int)))]
    compare = [(neural_network_output(network, example)[0], answer[0]) for example, answer in examples] # [list(tuple(float, int))]
    errors.append(sqrt((1.0/len(examples))*sum([pow(answer-output,2) for output, answer in compare]))) # [tuple(float, int)]

def train_network(network, examples, epochs): # network: [list(list(node))], examples: [list(tuple(list(int)))], epochs: [int]
    global errors
    errors = []                          # [list(float)]
    append_error(network, examples)      # []

    for epoch in range(epochs):          # [list(int)]
        for example, answer in examples: # [tuple(list(int))]
            output = neural_network_output(network, example) # [list(float)]
	    back_propagate_error(network, answer) # []
	    #print_weights(network)

	append_error(network, examples)         # []
     
#def print_weights(network):
#    for number, layer in enumerate(network[-2::-1]):
#        print 'layer', number
#        for node in layer: 
#	    print [link.weight for link in node.output]

alpha = 0.5                              # [float]

input_layer = [node([]) for n in range(10)] # [list(node)]
hidden_layer = [node(input_layer) for n in range(4)] # [list(node)]
output_layer = [node(hidden_layer) for n in range(1)] # [list(node)]

network = [input_layer, hidden_layer, output_layer] # [list(list(node))]

examples = [ ([1,0,0,1,1,2,0,1,0,0], [1]), # [list(tuple(list(int)))]
             ([1,0,0,1,2,0,0,0,2,2], [0]), # [tuple(list(int))]
	     ([0,1,0,0,1,0,0,0,3,0], [1]),      # [list(int)]
	     ([1,0,1,1,2,0,1,0,2,1], [1]),      # [tuple(list(int))]
 	     ([1,0,1,0,2,2,0,1,0,3], [0]),     # [tuple(list(int))]
	     ([0,1,0,1,1,1,1,1,1,0], [1]),      # [tuple(list(int))]
	     ([0,1,0,0,0,0,1,0,3,0], [0]),      # [list(int)]
	     ([0,0,0,1,1,1,1,1,2,0], [1]),      # [list(int)]
	     ([0,1,1,0,2,0,1,0,3,3], [0]),      # [list(int)]
	     ([1,1,1,1,2,2,0,1,1,1], [0]),      # [list(int)]
	     ([0,0,0,0,0,0,0,0,2,0], [0]),      # [list(int)]
	     ([1,1,1,1,2,0,0,0,3,2], [1]) ]     # [list(int)]

epochs = 1000                            # [int]
train_network(network, examples, epochs) # []
print [neural_network_output(network, example) for example, answer in examples] # [list(list(float))]

