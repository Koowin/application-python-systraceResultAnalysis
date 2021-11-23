import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

def cpu_graph(data, cpu_time, total_time):
    fig, ax = plt.subplots(figsize=(18,9))
    for i in range(0,len(data[0])):
        for x_1, x_2 in zip(data[0][i], data[1][i]):
            ax.add_patch(plt.Rectangle((x_1,i-0.5), x_2-x_1,0.5))
    ax.autoscale()
    ax.set_ylim(-1,len(data[0])+1)
    
    plt.text(1000000,len(data[0])+1.2, 'CPU use time: {}       Total time: {}       Proportion: {}'.format(cpu_time, total_time, cpu_time/total_time))
    plt.xlabel('time (μs)')
    plt.ylabel('CPU number')
    
    plt.show()

def disk_graph(data):
    y = np.arange(0, 4097, 1024)
    ax = plt.subplot()
    ax.plot(data[0], data[1], 'bo')
    
    plt.xlabel('time (μs)')
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%d byte'))
    plt.yticks(y)
    plt.show()

def database_graph(data):
    ax = plt.subplot()
    y = []
    for i in range(len(data)):
        y.append(1)
    ax.plot(data, y, 'bo')

    plt.xlabel('time (μs)')
    plt.show()

def average_graph(data):
    y = np.arange(4)
    types_string = ['Total', 'Disk', 'CPU', 'Database']
    values = [1]
    for item in data:
        if item[1] == 0:
            values.append(0)
        else:
            values.append(item[0] / item[1])
    
    plt.barh(y, values, color=['b', 'g', 'r', 'y'])
    plt.yticks(y, types_string)
    plt.ylabel('proportion')
    plt.text(values[1], 1, "value = {0:0.6f}, count = {1}".format(values[1], data[0][1]))
    plt.text(values[2], 2, "value = {0:0.6f}, count = {1}".format(values[2], data[1][1]))
    plt.text(values[3], 3, "value = {0:0.6f}, count = {1}".format(values[3], data[2][1]))

    plt.show()