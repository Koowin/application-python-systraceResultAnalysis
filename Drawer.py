import matplotlib.pyplot as plt

def cpu_graph(data):
    ax = plt.subplot()
    
    for i in range(0,len(data[0])):
        for x_1, x_2 in zip(data[0][i], data[1][i]):
            ax.add_patch(plt.Rectangle((x_1,i), x_2-x_1,0.5))
    ax.autoscale()
    ax.set_ylim(-1,len(data[0])+1)
    plt.show()

def disk_graph(data):
    ax = plt.subplot()
    ax.plot(data[0], data[1], 'bo')
    plt.show()