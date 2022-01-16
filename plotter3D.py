import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt


def update_graph(graph, step: int, frequency: int, total_steps: int, new_state: np.ndarray, filename):
    if step % frequency != 0:
        return
    # x, y, z = graph._verts3d
    x = list([s for s in range(new_state.shape[0])])
    z = list([min(list([1000*new_state[s][a] for a in range(new_state.shape[1])]))
              for s in range(new_state.shape[0])])
    y = list([step for _ in range(new_state.shape[0])])

    # graph.set_xdata(x)
    # graph.set_ydata(y)
    # graph.set_3d_properties(z)

    if step == total_steps - frequency:
        graph.scatter3D(x, y, z, color="red")
        plt.show()
        plt.draw()
        plt.gcf().savefig(filename, dpi=100)
    else:
        graph.scatter3D(x, y, z, color="green")


def update_graph_iteration(graph, step: int, frequency: int, total_steps: int, new_state: np.ndarray, filename):
    if step % frequency != 0:
        return
    # x, y, z = graph._verts3d
    x = list([s for s in range(new_state.shape[0])])
    z = list([new_state[s] for s in range(new_state.shape[0])])
    y = list([step for _ in range(new_state.shape[0])])

    # graph.set_xdata(x)
    # graph.set_ydata(y)
    # graph.set_3d_properties(z)

    if step == total_steps - frequency:
        graph.scatter3D(x, y, z, color="red")
        plt.show()
        plt.draw()
        plt.gcf().savefig(filename, dpi=100)
    else:
        graph.scatter3D(x, y, z, color="green")


def init_graph():
    graph = plt.axes(projection='3d')
    graph.set_xlabel("states")
    graph.set_ylabel("episode")
    graph.set_zlabel("value function x1e-3")
    graph.text2D(0.05, 0.95, "min value of q function according to action", transform=graph.transAxes)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5, forward=True)
    fig.set_dpi(100)
    return graph
