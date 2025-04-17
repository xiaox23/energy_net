import numpy as np
import os

def calculate_end_metrics(results_dir, strategies, num_nodes):
    """
    计算不同策略下所有节点在仿真结束时的 Qloss 和 Qsoc 的平均值和标准差。

    Args:
        results_dir (str): 仿真结果文件所在的目录。
        strategies (list): 策略名称列表 (如 ["Battery_Only", "Voltage_Control"])。
        num_nodes (int): 子节点的数量。

    Returns:
        dict: 包含每个策略下 Qloss 和 Qsoc 的平均值与标准差。
    """
    metrics = {}

    for strategy in strategies:
        Qloss_values = []
        Qsoc_values = []

        # 遍历所有节点，提取 Qloss 和 Qsoc 的最后一个时间步的值
        for node in range(num_nodes):
            result_file = os.path.join(results_dir, f"{strategy}_node_{node}_results.npy")
            if not os.path.exists(result_file):
                print(f"Warning: {result_file} does not exist!")
                continue

            # 加载结果文件
            data = np.load(result_file, allow_pickle=True).item()

            # 提取 Qloss 和 Qsoc 的最后一个时间步的值
            Qloss = data.get("Qloss", [])
            Qsoc = data.get("Qsoc", [])
            if len(Qloss) > 0 and len(Qsoc) > 0:
                Qloss_values.append(Qloss[-1])  # 仿真结束时的 Qloss
                Qsoc_values.append(Qsoc[-1])   # 仿真结束时的 Qsoc

        # 计算平均值和标准差
        metrics[strategy] = {
            "Qloss_avg": np.mean(Qloss_values) if Qloss_values else 0,
            "Qloss_std": np.std(Qloss_values) if Qloss_values else 0,
            "Qsoc_avg": np.mean(Qsoc_values) if Qsoc_values else 0,
            "Qsoc_std": np.std(Qsoc_values) if Qsoc_values else 0,
        }

    return metrics


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
    # 仿真结果所在目录
    results_dir = "paper_results/Task4_results_30d_ta2"
    num_nodes = 10  # 子节点数量
    strategies = ["Battery_Only", "Voltage_Control"]  # 策略列表

    # 保存结果到文本文件
    output_file = "simulation_metrics.txt"

    # 计算最终的平均值和标准差 (Qloss 和 Qsoc)
    metrics = calculate_end_metrics(results_dir, strategies, num_nodes)
    with open(output_file, "w") as f:  # 使用写入模式清空文件并写入第一部分
        f.write("End Metrics (Qloss and Qsoc):\n")
        for strategy, values in metrics.items():
            f.write(f"Strategy: {strategy}\n")
            f.write(f"  Qloss Average: {values['Qloss_avg']:.4f}\n")
            f.write(f"  Qloss Variability (Std): {values['Qloss_std']:.4f}\n")
            f.write(f"  Qsoc Average: {values['Qsoc_avg']:.4f}\n")
            f.write(f"  Qsoc Variability (Std): {values['Qsoc_std']:.4f}\n")
            f.write("-" * 50 + "\n")

    print(f"End Metrics saved to {output_file}")

    # 节点寿命和失败率计算
    failure_threshold = 0.5  # Qsoc threshold for node failure

    # 使用追加模式 ("a") 写入节点寿命和失败率
    with open(output_file, "a") as f:  # 追加到文件中
        f.write("\nNode Metrics (Lifetime and Failure Rate):\n")
        for method in strategies:
            metrics = calculate_node_metrics(results_dir, method, num_nodes, failure_threshold)
            f.write(f"Strategy: {method}\n")
            f.write(f"  Average Node Lifetime: {metrics['average_lifetime']:.2f} days\n")
            f.write(f"  Node Failure Rate: {metrics['failure_rate']:.2f}%\n")
            f.write("-" * 50 + "\n")

    print(f"Node Metrics appended to {output_file}")