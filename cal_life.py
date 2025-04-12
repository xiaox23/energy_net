import numpy as np
import os

def calculate_node_metrics(results_dir, method_prefix, total_nodes, failure_threshold=0.5):
    """
    Calculate Node Lifetime and Node Failure Rate for a specific method.

    Args:
        results_dir (str): Directory containing simulation results.
        method_prefix (str): Prefix of the method (e.g., "Battery_Only" or "Voltage_Control").
        total_nodes (int): Total number of nodes.
        failure_threshold (float): Qsoc threshold for node failure (default = 0.5).

    Returns:
        dict: Contains average node lifetime (in days), failure rate, and individual node lifetimes in days.
    """
    node_lifetimes = []
    failed_nodes = 0

    for node_id in range(total_nodes):
        file_path = os.path.join(results_dir, f"{method_prefix}_node_{node_id}_results.npy")
        
        # Check if the data file exists
        if not os.path.exists(file_path):
            print(f"Warning: Data for {method_prefix} node {node_id} not found.")
            continue

        # Load node data
        data = np.load(file_path, allow_pickle=True).item()
        Qsoc = data.get("Qsoc", [])  # Remaining energy
        P_demand = data.get("P_demand", [])  # Power consumption data

        # Validate data completeness
        if len(Qsoc) == 0 or len(P_demand) == 0:
            print(f"Warning: Incomplete data for {method_prefix} node {node_id}. Skipping...")
            continue

        # Calculate node lifetime
        lifetime = None
        for t, qsoc in enumerate(Qsoc):
            if qsoc <= failure_threshold:  # Node fails when Qsoc <= failure threshold
                lifetime = t  # Record the time step
                failed_nodes += 1  # Mark as a failed node
                break

        if lifetime is None:
            # If the node does not fail, lifetime is total simulation time
            lifetime = len(Qsoc)
        
        # Convert lifetime to days (1 day = 86400 seconds)
        node_lifetimes.append(lifetime / 86400)

    # Calculate metrics
    average_lifetime = np.mean(node_lifetimes) if node_lifetimes else 0
    failure_rate = (failed_nodes / total_nodes) * 100 if total_nodes > 0 else 0

    return {
        "method": method_prefix,
        "node_lifetimes": node_lifetimes,
        "average_lifetime": average_lifetime,
        "failure_rate": failure_rate
    }


if __name__ == "__main__":
    # Simulation results directory
    results_dir = "results_30d"
    total_nodes = 10  # Total number of nodes
    failure_threshold = 0.5  # Qsoc threshold for node failure

    # Methods to compare
    methods = ["Battery_Only", "Voltage_Control"]

    # Calculate metrics for each method
    for method in methods:
        metrics = calculate_node_metrics(results_dir, method, total_nodes, failure_threshold)
        print(f"Metrics for {method}:")
        print(f"  Average Node Lifetime: {metrics['average_lifetime']:.2f} days")
        print(f"  Node Failure Rate: {metrics['failure_rate']:.2f}%")
        print("-" * 50)