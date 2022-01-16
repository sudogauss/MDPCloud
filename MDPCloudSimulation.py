from typing import Union, Tuple, Callable, Any
import numpy as np
import random
from multiprocessing_decorator import multiprocessing_decorator


# We have a state space (m,n) in [0, b] x [1, k]. We represent them as s = m*k + n - 1
# We have an action space alpha(j) where j is in [1, k] and corresponds to maintain only j servers
# We have a probability distribution of packets arrival. We have maximum of l packets that can arrive
class MDPCloud:
    def __init__(self, queue_capacity: int, max_servers_num: int, max_arrivals: int,
                 server_flow: int, probability_distribution: Union[str, np.array],
                 cost_vm_run: int, cost_vm_activation: int, cost_vm_deactivation: int, cost_client: int):

        p = None

        if probability_distribution is str:
            if probability_distribution != "uniform":
                print("This distribution is not supported")
                raise "Distribution is not supported exception"
            p = np.array([1 / (max_arrivals + 1) for i in range(max_arrivals + 1)])
        else:
            p = probability_distribution

        self.queue_capacity = queue_capacity
        self.max_servers_num = max_servers_num
        self.max_arrivals = max_arrivals
        self.server_flow = server_flow
        self.probability_distribution = p
        self.cost_vm_run = cost_vm_run
        self.cost_vm_activation = cost_vm_activation
        self.cost_vm_deactivation = cost_vm_deactivation
        self.cost_client = cost_client
        self.set_params()
        self.transition_matrix, self.cost_matrix = MDPCloud. \
            define_transition_and_cost_matrix(MDPCloud, queue_capacity, max_servers_num, max_arrivals,
                                              server_flow, p, cost_vm_run, cost_vm_activation,
                                              cost_vm_deactivation, cost_client)

    def set_params(self, episodes: int = -1, max_game_steps: int = -1,
                   discount: float = -1.0, eps: float = -1.0, alpha: float = -1.0):

        self.episodes = episodes
        self.max_game_steps = max_game_steps
        self.discount = discount
        self.eps = eps
        self.alpha = alpha

    # indicator function
    @staticmethod
    def ind(a: int, b: int):
        if a > b:
            return 1
        return 0

    @staticmethod
    def calc_cost(cls, j: int, n: int, m: int, cf: int, ca: int, cd: int, ch: int) -> int:
        return j * cf + (j - n) * cls.ind(j, n) * ca + (n - j) * cls.ind(n, j) * cd + m * ch

    @staticmethod
    def define_transition_and_cost_matrix(cls, b: int, k: int, l: int, d: int, p: np.array,
                                          cf: int, ca: int, cd: int, ch: int) -> Tuple[
        np.ndarray, np.ndarray]:
        t = np.zeros([(b + 1) * k, (k + 1), (b + 1) * k])
        r = np.zeros([(b + 1) * k, (k + 1)])
        for m in range(b + 1):
            for n in range(1, k + 1):
                s = m * k + n - 1
                for i in range(1, k + 1):
                    for j in range(l + 1):
                        npr = i
                        mp = min(b, max(0, m + j - npr * d))
                        sp = mp * k + npr - 1
                        t[s][npr][sp] = t[s][npr][sp] + p[j]
                        r[s][npr] = cls.calc_cost(MDPCloud, npr, n, m, cf, ca, cd, ch)
        return t, r

    @staticmethod
    def get_random(distribution: np.array) -> int:
        x = random.random()
        s = 0.0
        for i in range(len(distribution)):
            if s <= x <= s + distribution[i]:
                return i
            s += distribution[i]
        return len(distribution) - 1

    @staticmethod
    def get_best_action(q: np.ndarray, s: int) -> Any:
        return 1 + np.argmin(np.array([q[s][a] for a in range(1, q.shape[1])]))

    @staticmethod
    def get_best_policy(cls, q: np.ndarray) -> np.array:
        return np.array([cls.get_best_action(q, s) for s in range(q.shape[0])])

    def show_best_policy(self, pi: np.array, filename=None) -> None:
        f = None
        if filename is not None:
            f = open(filename, 'w')
        for i in range(self.queue_capacity + 1):
            for j in range(1, self.max_servers_num + 1):
                print(f'In state ({i}, {j}) do: {pi[i * self.max_servers_num + j - 1]}')
                if f is not None:
                    f.write(f'In state ({i}, {j}) do: {pi[i * self.max_servers_num + j - 1]}')
                    f.write("\n")
        if f is not None:
            f.close()

    def value_iteration(self, callback: Callable[[Any, int, int, int, np.array, Any], None],
                        graph: Any, frequency: int, filename: Any) -> Tuple[np.ndarray, np.ndarray]:

        if self.episodes == -1 or self.discount == -1:
            raise "Can't execute. Minimum requirements are discount and episodes number. " \
                  "Set them via set_params function"

        v = np.zeros(shape=[self.transition_matrix.shape[0]])
        vp = np.zeros(shape=[self.transition_matrix.shape[0]])
        pi = np.zeros(shape=[self.transition_matrix.shape[0]])

        for i in range(self.episodes):
            for j in range(self.transition_matrix.shape[0]):
                v[j] = min(map(lambda x: sum(list([self.transition_matrix[j][x][sp] *
                                                   (self.cost_matrix[j][x] + self.discount * vp[sp])
                                                   for sp in range(self.transition_matrix.shape[0])])),
                               list(range(1, self.transition_matrix.shape[1]))))
            vp = v[:]
            callback(graph, i, frequency, self.episodes, v, filename)
        for s in range(self.transition_matrix.shape[0]):
            a = list(map(lambda x: sum(
                list([self.transition_matrix[s][x][sp] * (self.cost_matrix[s][x] + self.discount * v[sp])
                      for sp in range(self.transition_matrix.shape[0])])),
                         list(range(1, self.transition_matrix.shape[1]))))
            pi[s] = 1 + np.argmin(np.array(a))

        return pi, v

    def q_learning(self, max_reward: int, callback: Callable[[Any, int, int, int, np.array, Any], None], graph: Any,
                   frequency: int, filename: Any) -> np.ndarray:
        if self.episodes == -1 or self.eps == -1.0 or self.discount == -1.0 or self.alpha == -1 or self.max_game_steps == -1:
            raise "All parameters are required. Please set them via set_params function"

        q = max_reward * np.random.rand(self.cost_matrix.shape[0], self.cost_matrix.shape[1])
        for i in range(1, self.cost_matrix.shape[1]):
            q[self.cost_matrix.shape[0] - 1][i] = 0

        for i in range(self.episodes):
            s = 0
            j = 0
            while j < self.max_game_steps:
                action = 1 + MDPCloud.get_random(np.array([(1 / (self.cost_matrix.shape[1] - 1))
                                                           for _ in range(self.cost_matrix.shape[1] - 1)]))
                if random.uniform(0, 1) >= self.eps:
                    action = MDPCloud.get_best_action(q, s)
                arrivals = MDPCloud.get_random(self.probability_distribution)
                m = int(s // (self.cost_matrix.shape[1] - 1))
                mp = min((self.cost_matrix.shape[0] // (self.cost_matrix.shape[1] - 1) - 1),
                         max(0, m + arrivals - action * self.server_flow))
                sp = mp * (self.cost_matrix.shape[1] - 1) + action - 1
                q[s][action] = q[s][action] + self.alpha * (self.cost_matrix[s][action] - q[s][action] + self.discount *
                                                            min([q[sp][a] for a in
                                                                 range(1, self.cost_matrix.shape[1])]))
                s = sp
                j += 1
            callback(graph, i, frequency, self.episodes, q, filename)
        return q

    def sarsa(self, max_reward: int, callback: Callable[[Any, int, int, int, np.array, Any], None], graph: Any,
              frequency: int, filename: Any) -> np.ndarray:

        if self.episodes == -1 or self.eps == -1.0 or self.discount == -1.0 or self.alpha == -1 or self.max_game_steps == -1:
            raise "All parameters are required. Please set them via set_params function"

        q = max_reward * np.random.rand(self.cost_matrix.shape[0], self.cost_matrix.shape[1])
        for i in range(1, self.cost_matrix.shape[1]):
            q[self.cost_matrix.shape[0] - 1][i] = 0

        for i in range(self.episodes):
            s = 0
            j = 0
            while j < self.max_game_steps and s != (self.cost_matrix.shape[0] - 1):
                action = 1 + MDPCloud.get_random(np.array([(1 / (self.cost_matrix.shape[1] - 1))
                                                           for _ in range(self.cost_matrix.shape[1] - 1)]))
                if random.uniform(0, 1) >= self.eps:
                    action = MDPCloud.get_best_action(q, s)
                arrivals = MDPCloud.get_random(self.probability_distribution)
                m = int(s // (self.cost_matrix.shape[1] - 1))
                mp = min((self.cost_matrix.shape[0] // (self.cost_matrix.shape[1] - 1) - 1),
                         max(0, m + arrivals - action * self.server_flow))
                sp = mp * (self.cost_matrix.shape[1] - 1) + action - 1
                action_p = 1 + MDPCloud.get_random(np.array([(1 / (self.cost_matrix.shape[1] - 1))
                                                             for _ in range(self.cost_matrix.shape[1] - 1)]))
                if random.uniform(0, 1) >= self.eps:
                    action_p = MDPCloud.get_best_action(q, sp)
                q[s][action] = q[s][action] + self.alpha * (self.cost_matrix[s][action] - q[s][action] +
                                                            self.discount * q[sp][action_p])
                s = sp
                j += 1
            if s == (self.cost_matrix.shape[0] - 1):
                print("Lost, in the game")
            callback(graph, i, frequency, self.episodes, q, filename)
        return q
