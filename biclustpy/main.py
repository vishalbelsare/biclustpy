from . import helpers
from . import ilp

class Algorithm:
    
    """
    Class to select algorithm for solving the subproblems.
    
    Attributes:
        algorithm_name (string): Name of selected algorithm. Must be either \"ILP\", \"FP\", or \"EDGE-DEL\". Default = \"ILP\".
        ilp_time_limit (float): Time limit for algorithm \"ILP\" in seconds. If <= 0, no time limit is enforced. Default = 60.
        ilp_tune (bool): If True, the model generated by \"ILP\" is tuned before being optimized. Default = False.
    """
    
    def __init__(self):
        self.algorithm_name = "ILP"
        self.ilp_time_limit = 60
        self.ilp_tune = False
            
    def run(self, weights, threshold, subgraph):
        """
        Runs the selected algorithm on a given subgraph.
        
        Args:
            weights (numpy.array): The overall problem instance.
            threshold (float): Edges whose weights are below the threshold are absent.
            subgraph (networkx.Graph): The subgraph of the instance that should be rendered bi-transitive.
        
        Returns:
            networkx.Graph: The obtained bi-transitive subgraph.
            float: Objective value of obtained solution.
            bool: True if and only if obtained solution is guaranteed to be optimal.
        """
        if self.algorithm_name == "ILP":
            return ilp.run(weights, threshold, subgraph, self.ilp_time_limit, self.ilp_tune)
        elif self.algorithm_name == "FP":
            raise Exception("The algorithm FP has not been implemented yet.") 
        elif self.algorithm_name == "EDGE-DEL":
            raise Exception("The algorithm EDGE-DEL has not been implemented yet.")
        else:
            raise Exception("Invalid algorithm name \"" + self.algorithm_name + "\". Must be either \"ILP\", \"FP\", or \"EDGE-DEL\".")
    
    
def compute_bi_clusters(weights, threshold, algorithm):
    """
    Computes bi-clusters. First decomposed the instance into connected components and then calls user-specified algorithm so solve the subproblems.
    
    Args:
        weights (numpy.array): The problem instance.
        threshold (float): Edges whose weights are below the threshold are absent.
        algorithm (Algorithm): The subgraph that should be rendered bi-transitive.
    
    Returns:
        list of tuple of list of int: List of computed bi-clusters. The first element of each bi-cluster is the list of rows, the second the list of columns. 
        float: Objective value of the obtained solution.
        bool: True if and only if the obtained solution is guaranteed to be optimal.
    """
    
    # Get dimension of the problem instance and build NetworkX graph.
    num_rows = weights.shape[0]
    num_cols = weights.shape[1]
    graph = helpers.build_graph_from_weights(weights, threshold, range(num_rows + num_cols))
    
    # Initialize the return variable.
    bi_clusters = []
    
    # Decompose graph into connected components and check if some 
    # of them are already bi-cliques. If so, put their rows and columns 
    # into bi-clusters. Otherwise, add the connected 
    # component to the list of connected subgraphs that have to be 
    # rendered bi-transitive.
    subgraphs = []
    components = helpers.connected_components(graph)
    for component in components:
        if helpers.is_bi_clique(component, num_rows):
            bi_cluster = ([], [])
            for node in component.nodes:
                if helpers.is_row(node, num_rows):
                    bi_cluster[0].append(node)
                else:
                    bi_cluster[1].append(helpers.node_to_col(node, num_rows))
            bi_clusters.append(bi_cluster)
        else:
            subgraphs.append(component)
            
    # Print information about connected components.
    print("\n==============================================================================")
    print("Finished pre-processing.")
    print("==============================================================================")
    print("Number of connected components: " + str(len(components)))
    print("Number of bi-cliques: " + str(len(bi_clusters)))
    print("==============================================================================")
    
    # Solve the subproblems and construct the final bi-clusters. 
    # Also compute the objective value and a flag that indicates whether the
    # obtained solution is guaranteed to be optimal.
    obj_val = 0
    is_optimal = True 
    counter = 0
    for subgraph in subgraphs:
        counter = counter + 1
        print("\n==============================================================================")
        print("Solving subproblem " + str(counter) + " of " + str(len(subgraphs)) + ".")
        print("==============================================================================")
        print("Number of nodes: " + str(subgraph.number_of_nodes()))
        bi_transitive_subgraph, local_obj_val, local_is_optimal = algorithm.run(weights, threshold, subgraph)
        obj_val = obj_val + local_obj_val
        is_optimal = is_optimal and local_is_optimal
        for component in helpers.connected_components(bi_transitive_subgraph):
            if not helpers.is_bi_clique(component, num_rows):
                msg = "Subgraph should be bi-clique but isn't.:"
                msg = msg + "\nNodes: " + str(component.nodes)
                msg = msg + "\nEdges: " + str(component.edges)
                raise Exception(msg)
            bi_cluster = ([], [])
            for node in component.nodes:
                if helpers.is_row(node, num_rows):
                    bi_cluster[0].append(node)
                else:
                    bi_cluster[1].append(helpers.node_to_col(node, num_rows))
            bi_clusters.append(bi_cluster)
        print("==============================================================================")
    
    print("\n==============================================================================")
    print("Finished computation of bi-clusters.")
    print("==============================================================================")
    print("Objective value: " + str(obj_val))
    print("Is optimal: " + str(is_optimal))
    print("Number of bi-clusters: " + str(len(bi_clusters)))
    print("==============================================================================")
    
    
    # Return the obtained bi-clusters, the objective value of the obtained solution, 
    # and a flag that indicates if the solution is guaranteed to be optimal.
    return bi_clusters, obj_val, is_optimal 