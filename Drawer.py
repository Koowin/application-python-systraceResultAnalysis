import matplotlib.pyplot as plt
import numpy as np

def draw_graph(x, y, items, this_ratio):
    sum_ratio = 0
    for item in items:
        sum_ratio += float(item['operating_ratio'])
    avg_ratio = sum_ratio / len(items)

    plt.figure(figsize=(15,8))
    plt.subplot(211)
    plt.plot(x, y, 'bo')
    plt.xlabel('Time (μs)', labelpad=15)
    plt.ylabel('Size (byte)', labelpad=15)

    xnp = np.arange(2)
    plt.subplot(212)
    plt.bar(xnp, [this_ratio, avg_ratio], color=['r','g'])
    plt.xticks(xnp, ['This', 'AVG'])

    plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.5)
    plt.show()