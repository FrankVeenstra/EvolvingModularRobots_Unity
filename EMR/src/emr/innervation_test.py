from encoding import robot_graph
from encoding import LSystem
from encoding import direct_encoding
from emr.controller import custom_controller
from emr.controller import phase_coupled_oscillator
from emr.controller import decentralized_controller
from stats import graph_visualizer


import numpy as np
if __name__ == "__main__":
    from config import config_handler
    cfg = config_handler.make_config()
    ctrlr = phase_coupled_oscillator.PhaseCoupledOscillator
    l = LSystem.GraphGrammar(ctrlr,cfg)    
    d = direct_encoding.DirectEncoding(ctrlr,cfg)
    actions = np.ndarray(shape=(1,50),dtype=np.float32)
    sensory_input = np.ndarray(shape=(1,50),dtype=np.float32)
    print("LSystem: ")
    bp = l.get_graph()
    ns = decentralized_controller.innervate_modules(bp)
    bp.print()
    bp.step(sensory_input,actions, 0.1)
    #graph_visualizer.visualize(bp)
    ax = None
    import matplotlib.pyplot as plt
    STEPS = 1
    for i in range(100):
        print("LSystem: ")
        l = LSystem.GraphGrammar(ctrlr,cfg)   
        bp = l.get_graph()
        ns = decentralized_controller.innervate_modules(bp)
        bp.print()
        ax, vg = graph_visualizer.visualize(bp,ax)
        for j in range(STEPS):
            bp.step(sensory_input,actions, 0.02)
            ax,vg = graph_visualizer.visualize(bp, ax, vg)
            plt.pause(0.0001)
        continue
        print("Direct Encoding: ")
        for j in range(5):
            d.mutate(0.5,0.3,0.3)
        bp = d.genome
        ns = decentralized_controller.innervate_modules(bp)
        bp.print()

        ax, vg = graph_visualizer.visualize(bp,ax)
        for j in range(STEPS):
            bp.step(sensory_input,actions, 1)
            ax,vg = graph_visualizer.visualize(bp, ax, vg)
            plt.pause(0.0001)
        #print("Direct Encoding: ")
        #bp = d.genome
        #ns = decentralized_controller.innervate_modules(bp)
        #bp.print()
    plt.show()

    pass
