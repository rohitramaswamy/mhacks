import numpy as np

class KServerLoadBalancer:
    def __init__(self, k, server_weights):
        """
        Initialize the load balancer.
        
        Parameters:
        k: Number of servers
        server_weights: List of weights for each server. Lower weight means server is favored.
        """
        self.k = k  # number of servers
        self.server_weights = server_weights  # weights of the servers
        self.server_loads = [0] * k  # all servers start with zero load

    def get_weighted_probabilities(self):
        """
        Compute the probabilities of each server being selected based on weights.
        Servers with lower weights are more likely to be selected.
        """
        weights_inv = [1 / w for w in self.server_weights]
        total = sum(weights_inv)
        probabilities = [w / total for w in weights_inv]
        return probabilities

    def assign_task(self, task_load):
        """
        Randomly assign a task to a server based on weighted probabilities.
        
        Parameters:
        task_load: The load that the task adds to a server.
        """
        probabilities = self.get_weighted_probabilities()
        selected_server = np.random.choice(self.k, p=probabilities)
        
        # Assign the task's load to the selected server
        self.server_loads[selected_server] += task_load
        
        print(f"Assigned task of load {task_load} to server {selected_server + 1}")
        return selected_server

    def serve_tasks(self, tasks):
        """
        Serve multiple tasks.
        
        Parameters:
        tasks: List of task loads to be assigned to servers.
        """
        for task in tasks:
            self.assign_task(task)
        
        # Output the final loads of each server
        print("\nFinal loads on each server:")
        for i, load in enumerate(self.server_loads):
            print(f"Server {i + 1}: {load} load units")

# Example usage
k = 5  # number of servers
#  [Cleveland, Vegas, Tampa, Boston, Ann Arbor]
server_weights = [3.5965998, 3.990588, 3.7214596, 4.200251, 3.6135137]  # weights of servers (lower weight = more preferred)

# Initialize the load balancer, server_weights come from our ML model
load_balancer = KServerLoadBalancer(k, server_weights)

# Example tasks with different loads
tasks = [5, 3, 7, 2, 10, 4,5, 3, 7, 2, 10, 4,5, 3, 7, 2, 10, 4,5, 3, 7, 2, 10, 4,5, 3, 7, 2, 10, 4]

# Distribute tasks across servers
load_balancer.serve_tasks(tasks)