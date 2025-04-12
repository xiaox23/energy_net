import numpy as np
import os

def calculate_node_metrics(results_dir, total_nodes, Q_total, failure_threshold=0):
    """
    计算 Node Lifetime 和 Node Failure Rate。

    Args:
        results_dir (str): 存储仿真结果的目录。
        total_nodes (int): 节点总数。
        Q_total (float): 电池的初始容量（单位：Ah）。
        failure_threshold (float): 节点失败的 Qsoc 阈值（默认 = 0）。

    Returns:
        dict: 包括 Node Lifetime 和 Node Failure Rate 的结果。
    """
    node_lifetimes = []
    failed_nodes = 0

    for node_id in range(total_nodes):
        file_path = os.path.join(results_dir, f"Battery_Only_node_{node_id}_results.npy")
        if not os.path.exists(file_path):
            print(f"Warning: Data for node {node_id} not found.")
            continue

        # 加载节点数据
        data = np.load(file_path, allow_pickle=True).item()
        Qloss = data.get("Qloss", [])  # 累积能量损失
        Qsoc = data.get("Qsoc", [])    # 剩余电量
        avg_power = np.mean(data.get("P_demand", []))  # 平均功耗

        # 检查数据是否完整
        if len(Qloss) == 0 or len(Qsoc) == 0 or avg_power == 0:
            print(f"Warning: Incomplete data for node {node_id}. Skipping...")
            continue

        # 计算节点寿命
        final_Qloss = Qloss[-1]  # 仿真结束时的 Qloss
        lifetime = (Q_total - final_Qloss) / avg_power
        node_lifetimes.append(lifetime)

        # 检查节点是否失败
        if Qsoc[-1] <= failure_threshold:  # 如果剩余电量小于等于阈值，则认为节点失败
            failed_nodes += 1

    # 计算 Node Failure Rate
    failure_rate = (failed_nodes / total_nodes) * 100

    # 返回结果
    return {
        "node_lifetimes": node_lifetimes,
        "average_lifetime": np.mean(node_lifetimes) if node_lifetimes else 0,
        "failure_rate": failure_rate
    }


if __name__ == "__main__":
    # 仿真结果存储目录
    results_dir = "results"
    total_nodes = 10  # 子节点总数（从 Task1.py 中获取）
    Q_total = 3.0  # 电池总容量（单位：Ah，从 Task1.py 中获取）
    failure_threshold = 0.45  # 节点失败的 Qsoc 阈值，默认为 0%

    # 计算节点寿命和失败率
    metrics = calculate_node_metrics(results_dir, total_nodes, Q_total, failure_threshold)

    # 输出结果
    print("Node Lifetime and Failure Rate Metrics:")
    print(f"  Average Node Lifetime: {metrics['average_lifetime']} hours")
    print(f"  Node Failure Rate: {metrics['failure_rate']}%")