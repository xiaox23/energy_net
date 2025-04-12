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


if __name__ == "__main__":
    # 仿真结果所在目录
    results_dir = "results"
    num_nodes = 10  # 子节点数量
    strategies = ["Battery_Only", "Voltage_Control"]  # 策略列表

    # 计算最终的平均值和标准差
    metrics = calculate_end_metrics(results_dir, strategies, num_nodes)

    # 输出结果
    for strategy, values in metrics.items():
        print(f"Strategy: {strategy}")
        print(f"  Qloss Average: {values['Qloss_avg']}")
        print(f"  Qloss Variability (Std): {values['Qloss_std']}")
        print(f"  Qsoc Average: {values['Qsoc_avg']}")
        print(f"  Qsoc Variability (Std): {values['Qsoc_std']}")