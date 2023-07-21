import numpy as np
import matplotlib.pyplot as plt
import pickle 

class StatisticsLogger:
    def __init__(self, experiment_path : str):
        self.experiment_path = experiment_path
        self.data = []
    def append_data(self, value):
        self.data.append(value)

    def save(self, filename : str):
        with open(f'{self.experiment_path}{filename}.pcl', 'wb') as fp:
            pickle.dump(self.data, fp)

    def load(self, filename : str):
        with open(f'{self.experiment_path}{filename}.pcl','rb') as fp:
            self.data = pickle.load(fp)

    def get_max(self):
        max = []
        for i,g in enumerate(self.data):
            max.append(np.max(g))
        return max

    def plot_average(self, ax):
        avg = []
        max = [] 
        min = []
        l_a = []
        h_a = []
        tf = []
        sf = []
        x = []
        for i,g in enumerate(self.data):
            x.append(i)
            avg.append(np.average(g))
            max.append(np.max(g))
            min.append(np.min(g))
            tf.append(np.quantile(g,0.25))
            sf.append(np.quantile(g,0.75))
            l_a.append(np.quantile(g,0.1))
            h_a.append(np.quantile(g,0.9))
        ax.plot(max, c="b")
        ax.fill_between(x, tf,sf, alpha = 0.2, color="b")
        ax.fill_between(x, min, max, alpha = 0.04, color="b")
        ax.fill_between(x, min, max, alpha = 0.1, color="b")
       
    
if __name__ == "__main__":
    fig, axs = plt.subplots(5, 4, constrained_layout=True, figsize=(10, 10))
    for i in range(16):
        stats = StatisticsLogger(f"TestRuns3/exp{i}/")
        stats.load("stats")
        row = i % 5
        stats.plot_average(axs[row, int(i/5)])
    plt.show()
