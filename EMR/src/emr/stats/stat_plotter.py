import stats.StatisticsLogger as st
import matplotlib.pyplot as plt
from matplotlib import cm
from tqdm import tqdm
import numpy as np

def clamp_data(data, gen : int = 90):
    newdata = []
    for i in range(len(data)):
        if (i > gen):
            break
        newdata.append(data[i])
    return newdata

def plot_average(ax, data, color = "black", label = "no label"):
    #return
    dat = np.array(data)
    mean = dat.mean(axis=0)
    p25 = np.percentile(dat,25,axis = 0)
    p75 = np.percentile(dat,75, axis = 0)
    x= np.arange(0,len(p25))
    for d in data:
        ax.plot(d,color=color, alpha=0.1)
    ax.fill_between(x,p25,p75,color = color, alpha = 0.1)
    try:
        ax.plot(mean,color=color, label = label)
    except:
        print("Could not plot the max average of the runs. Likely that some runs did not complete")
    ax.legend()

def load_multiple_runs():
    fig, axs = plt.subplots(1, 1, constrained_layout=True, figsize=(10, 10))
    #runs = ['run_0.005','run_0.01','run_0.02','run_0.04','run_0.08','run_0.16','run_0.32','run_0.64']
    runs = ['nsga_0.005','nsga_0.01','nsga_0.02','nsga_0.04','nsga_0.16','nsga_0.32','nsga_0.64']
    #runs = ['run_0.01']
    n_experiments = 10
    cmap = cm.get_cmap('magma')
    for n, run in tqdm(enumerate(runs)):
        color = cmap((float(n)/(len(runs)-1)))
        data= [] 
        for i in range(n_experiments):
            stats = st.StatisticsLogger(f"TestRuns/{run}/exp{i}/")
            stats.load("stats")
            data.append(clamp_data(stats.get_max()))
            #row = i % 5
            #stats.plot_average(axs[row, int(i/5)])
        plot_average(axs, data, color = color, label=run)        
    plt.show()

def load_single(path):
    fig, ax = plt.subplots(1, 1, constrained_layout=True, figsize=(10, 10))
    stats = st.StatisticsLogger(f"{path}")
    stats.load("stats")
    stats.plot_average(ax)
    plt.show()

if __name__ == "__main__":
    load_multiple_runs()
    #load_single("exp0/")
