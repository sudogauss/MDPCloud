import numpy as np
from MDPCloudSimulation import MDPCloud
import plotter3D as plotter
import matplotlib.pyplot as plt
import sys
import yaml

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

    cloud_simulator = None
    algo = "value_iteration"

    if len(sys.argv) == 1:
        cloud_simulator = MDPCloud(b, k, l, d, pa, cf, ca, cd, ch)
        cloud_simulator.set_params(5000, 70, 0.8, 0.2, 0.6)
    elif len(sys.argv) == 2:
        cloud_simulator = MDPCloud(b, k, l, d, pa, cf, ca, cd, ch)
        cloud_simulator.set_params(5000, 70, 0.8, 0.2, 0.6)
        algo = sys.argv[1]
    elif len(sys.argv) == 3:
        algo = sys.argv[1]
        f = sys.argv[2]
        with open(f, 'r') as stream:
            data = yaml.safe_load(stream)
        cloud_simulator = MDPCloud(data['params']['b'], data['params']['k'], data['params']['l'], data['params']['d'],
                                   data['params']['pa'], data['params']['cf'], data['params']['ca'], data['params']['cd'],
                                   data['params']['ch'])
        cloud_simulator.set_params(data['learning']['episodes'], data['learning']['max_game_steps'],
                                   data['learning']['discount'], data['learning']['eps'], data['learning']['alpha'])
    else:
        print("Incorrect number of arguments")
        sys.exit(1)

    graph = plotter.init_graph()

    try:
        if algo == "value_iteration":
            pi, v = cloud_simulator.value_iteration(plotter.update_graph_iteration, graph, 20, "output/value_graph.png")
            cloud_simulator.show_best_policy(pi, "output/value_policy.txt")
            print("===== value matrix =====")
            print(v)

        elif algo == "q_learning":
            q = cloud_simulator.q_learning(100, plotter.update_graph, graph, 200, "output/q_learning_graph.png")
            pi = MDPCloud.get_best_policy(MDPCloud, q)
            cloud_simulator.show_best_policy(pi, "output/q_learning_policy.txt")
            print("===== q matrix =====")
            print(q)

        elif algo == "sarsa":
            q = cloud_simulator.sarsa(100, plotter.update_graph, graph, 200, "output/sarsa_graph.png")
            pi = MDPCloud.get_best_policy(MDPCloud, q)
            cloud_simulator.show_best_policy(pi, "output/sarsa_policy.txt")
        else:
            print("Not supported algorithm")
            print("Please choose between: value_iteration, q_learning and sarsa")
    except RuntimeError as err:
        print(str(err))

