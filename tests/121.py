
class node:                              # activation: [int]*
    def __init__(self, input):
        pass

def neural_network_output(network, input): # network: [list(list(node))], input: [list(int)]
    for node in network[0]:                 # [list(node)]
        node.activation = 1              # [int]

    for index, node in enumerate(network[0]): # [tuple2(int, node)]
        node.activation = input[index]   # [int]

    return [node.activation for node in network[0]] # [list(int)]

input_layer = [node([]) for n in range(10)] # [list(node)]
hidden_layer = [node(input_layer) for n in range(4)] # [list(node)]
output_layer = [node(hidden_layer) for n in range(1)] # [list(node)]

network = [input_layer, hidden_layer, output_layer] # [list(list(node))]

examples = [ ([1,0,0,1,1,2,0,1,0,0], [1]), # [list(tuple2(list(int), list(int)))]
             ([1,0,0,1,2,0,0,0,2,2], [0]) ] # [list(int)]

print [neural_network_output(network, example) for example, answer in examples] # [list(list(int))]

