import networkx as nx
# import matplotlib.pyplot as plt
from collections import defaultdict


# read drone log
filename = '15-06-2018'
# filename = 'area' # no anomaly
# filename = 'CameraLogCurText' # very bad shape
# filename = 'nfz'
with open(filename + '.txt') as f:
	lines = f.readlines()

# define events
events = []
with open(filename + '-event.txt') as f:
	for line in f:
		print(line)
		events.append(line.rstrip())

# define events dictionary
events_dict = {}
for index, event in enumerate(events):
	events_dict[event] = index

# define node labels
node_labels = {}
for index, event in enumerate(events):
	node_labels[index] = event

# convert events to list of nodes 
nodes_events = []
for index, event in enumerate(events):
	nodes_events.append((index, {'event': f"{str(index)}. {event}"}))

# create graph
G = nx.MultiDiGraph()

# add nodes
G.add_nodes_from(nodes_events)

# get list of event id
log_event_id = []
node_members = defaultdict(list)
line_id = 0
for line in lines:
	for event in events:
		if event in line:
			event_id = events_dict[event]
			log_event_id.append(event_id)
			node_members[event_id].append(line_id)
			break
	
	line_id += 1

# print node members
# for event_id, member in node_members.items():
#	print(event_id, member)	

# create edges
edges_list = []
edges_weight = defaultdict(int)
log_event_id_len = len(log_event_id)
for index, event_id in enumerate(log_event_id):
	if (index+1) < log_event_id_len:	
		edges_list.append((event_id, log_event_id[index+1]))
		edges_weight[(event_id, log_event_id[index+1])] += 1

# create edges with weight
edges_weight_list = []
for edge, weight in edges_weight.items():
	edges_weight_list.append((edge[0], edge[1], {'weight': weight}))

# print(edges_weight_list)

# add edges to graph
G.add_edges_from(edges_weight_list)

# node colors
node_colors = []
anomalous_nodes = []	# nfz: 1,7	# 15-06-2018: 1
for index, event in node_labels.items():
	if index not in anomalous_nodes:
		node_colors.append('blue')
	else:
		node_colors.append('red')

# path from source node to destination
source = 0
destination = 4
for path in nx.all_simple_paths(G, source=source, target=destination):
   print(path)

# write to graphml
nx.write_graphml_lxml(G, filename + '.graphml')

# plot the graph
# pos = nx.kamada_kawai_layout(G)
# nx.draw_kamada_kawai(G, labels=node_labels, with_labels=True, font_size=6, node_size=150, node_color=node_colors)
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edges_weight, font_size=6)
# plt.show()
