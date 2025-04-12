import numpy as np
import matplotlib.pyplot as plt
import os

def visualize_combined_results(results_dir, save_dir="visualizations_combined"):
    """
    将所有编号相同的节点的相同物理量绘制在同一个子图上。
    
    Args:
        results_dir (str): 保存仿真结果的目录。
        save_dir (str): 保存可视化图像的目录。
    """
    # 确保保存目录存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 存储每个物理量的所有节点数据
    metrics = {
        "Qloss": [],
        "Qvoc": [],
        "Qsoc": [],
        "Qsc": [],
        "P_bat": [],
        "P_sc": [],
        "P_demand": []
    }

    # 遍历结果文件，加载数据
    for file_name in os.listdir(results_dir):
        if file_name.endswith(".npy") and "node" in file_name:
            file_path = os.path.join(results_dir, file_name)
            data = np.load(file_path, allow_pickle=True).item()

            # 将每个物理量的数据存入对应列表
            for metric in metrics.keys():
                metrics[metric].append(data[metric])

    # 获取时间步的长度（假设所有节点的时间步相同）
    time_steps = len(metrics["Qloss"][0])
    time = np.arange(time_steps)  # 时间步

    # 绘制每个物理量的图像
    plt.figure(figsize=(16, 20))  # 设置画布大小
    for i, (metric, values) in enumerate(metrics.items()):
        plt.subplot(4, 2, i + 1)  # 创建子图

        # 遍历每个节点的数据
        for node_id, node_values in enumerate(values):
            plt.plot(time, node_values, label=f"Node {node_id}")

        plt.title(metric)
        plt.xlabel("Time Step")
        plt.ylabel(metric)
        plt.legend(loc="upper right", fontsize="small", ncol=2)  # 显示图例
        plt.grid()

    # 调整布局
    plt.tight_layout()

    # 保存图像
    save_path = os.path.join(save_dir, "combined_visualization.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved combined visualization to {save_path}")


if __name__ == "__main__":
    results_dir = "results"
    save_dir = "visualizations_combined"

    # 生成组合可视化图像
    visualize_combined_results(results_dir, save_dir=save_dir)