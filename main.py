import numpy as np
from MDPCloudSimulation import MDPCloud
import plotter3D as plotter
import matplotlib.pyplot as plt

if __name__ == "__main__":
    b = 20
    k = 3
    d = 1
    pa = np.array([(1 / 3) for i in range(3)])
    l = 2
    cf = 1
    ca = 1
    cd = 1
    ch = 1

    cloud_simulator = MDPCloud(b, k, l, d, pa, cf, ca, cd, ch)
    cloud_simulator.set_params(5000, 70, 0.8, 0.2, 0.6)
    graph = plotter.init_graph()
    try:
        # pi, v = cloud_simulator.value_iteration(plotter.update_graph_iteration, graph, 20, "output/value_graph.png")
        # cloud_simulator.show_best_policy(pi, "output/value_policy.txt")

        # q = cloud_simulator.q_learning(100, plotter.update_graph, graph, 200, "output/q_learning_graph.png")
        # pi = MDPCloud.get_best_policy(MDPCloud, q)
        # cloud_simulator.show_best_policy(pi, "output/q_learning_policy.txt")

        q = cloud_simulator.sarsa(100, plotter.update_graph, graph, 200, "output/sarsa_graph.png")
        pi = MDPCloud.get_best_policy(MDPCloud, q)
        cloud_simulator.show_best_policy(pi, "output/sarsa_policy.txt")
    except RuntimeError as err:
        print(str(err))

