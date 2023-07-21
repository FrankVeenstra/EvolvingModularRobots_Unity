import math
import matplotlib.pyplot as plt
import matplotlib

class VisualGraph:
    class VNode:
        def __init__(self, name : str, parent :str, x, y, angle, depth: float = 1.0,descending_color = 0, ascending_color = 0):
            self.name = name
            self.parent = parent
            self.x = x
            self.y = y
            self.angle = angle
            self.depth = depth
            self.descending_color = matplotlib.colormaps['viridis'](0.5+(0.5* descending_color))
            self.ascending_color = matplotlib.colormaps['viridis'](0.5+(0.5* ascending_color))

    def __init__(self):
        self.vnodes = dict()

    def add_node(self,name,parent, connection_site: int, depth :float = 1, descending_color = 0, ascending_color = 0):
        angle = 0.0
        parent_angle = 0.0
        parent_position = [0,0]
        if (parent != None):
            angle = (connection_site-1) * math.pi*0.66 * (1.0/self.vnodes[parent].depth)
            parent_angle = self.vnodes[parent].angle
            parent_position = [self.vnodes[parent].x,self.vnodes[parent].y]
        
        angle = parent_angle + angle
        position_x = parent_position[0] + math.sin(angle)
        position_y = parent_position[1] + math.cos(angle)

        self.vnodes.update({name:VisualGraph.VNode(name, parent, position_x, position_y, angle,depth, descending_color = descending_color, ascending_color = ascending_color)})

def visualize(graph, ax = None, vg = None, plot_nerves = True, plot_controllers = True):
    cmap = "viridis"
    from encoding import robot_graph
    if (ax == None):
        fig = plt.figure(figsize=[8,8])
        ax = fig.add_subplot()
    ax.clear()
    queue = ['root']
    count = 0
    if (vg == None):
        #construct tree
        vg = VisualGraph()
        vg.add_node('root',None, None)

        while (len(queue) > 0):
            node = queue.pop()
            children = robot_graph.Blueprint.get_children(node,graph.nodes)
        
            for c in children:
                c_node = graph.nodes[c]
                parent = vg.vnodes[node]
                # add the node to the visual nodes
                ascending_color = graph.innervation[c].parents[node].value
                descending_color = graph.innervation[node].children[c].value
                vg.add_node(c, c_node.parent, int(c_node.connection_site), depth = parent.depth+1, descending_color = descending_color, ascending_color = ascending_color)
            
                queue.append(c)
            count+=1
    
    # plot 
    for n in vg.vnodes:
        node = vg.vnodes[n]
        node_color_value = graph.innervation[n].output_buffer[0]
        #color = matplotlib.colormaps[cmap](math.sqrt(math.pow(node.x,2) + math.pow(node.y,2))*0.25)
        color = matplotlib.colormaps[cmap](0.5+(0.5*node_color_value))
        ax.scatter([node.x],[node.y], c=color)
        if (node.parent):
            parent = vg.vnodes[node.parent]
            x = [node.x,parent.x]
            y = [node.y,parent.y]
            # ax.plot(x,y, c='black')
            if (plot_nerves):
                head_width = 0.1
                dx = (parent.x-node.x) * 0.8
                dy = (parent.y-node.y) * 0.8
                angle = math.atan2(dy,dx)
                scalar = 0.08
                vec = [math.cos(angle + math.pi/2) * scalar + dx/8, math.sin(angle+math.pi/2) * scalar+dy/8] 
                # descending nerve
                dnc = node.descending_color
                ax.arrow(node.x + vec[0], node.y+vec[1], dx, dy, color = dnc,head_width=head_width, length_includes_head=True)
                dx = (node.x-parent.x) * 0.8
                dy = (node.y-parent.y) * 0.8
                anc = parent.ascending_color
                ax.arrow(parent.x-vec[0], parent.y-vec[1], dx, dy, color = anc,head_width=head_width, overhang=-0.2, length_includes_head=True)
        ax.set_ylim([-7.5,7.5])
        ax.set_xlim([-7.5,7.5])
    # display nodes
    return ax,vg
    print(count)

if __name__ == "__main__":
    from encoding import LSystem
    for i in range(10):
        l = LSystem.GraphGrammar(3)
        for i in range(4):
            l.iterate()
        import graph_visualizer as gv
        gv.visualize(l)
    plt.show()
