import numpy as np
import matplotlib.pyplot as plt
import os

def visualize_node_comparison(results_dir, save_dir="visualizations"):
    """
    将相同节点的不同能量管理方式绘制在一个大图中，每个节点一张图。
    
    Args:
        results_dir (str): 保存仿真结果的目录。
        save_dir (str): 保存可视化图像的目录。
    """
    # 确保保存目录存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 解析结果目录中的文件名，按节点分组结果文件
    node_files = {}
    for file_name in os.listdir(results_dir):
        if file_name.endswith(".npy") and "node" in file_name:
            # 提取节点编号和策略名称
            parts = file_name.split("_")
            try:
                node_index = parts.index("node")  # 找到 "node" 在文件名中的位置
                node_id = int(parts[node_index + 1])  # 提取 "node" 后的编号
                strategy = "_".join(parts[:node_index])  # 组合 "node" 前的部分作为策略名称
            except (ValueError, IndexError):
                print(f"Skipping file with unexpected format: {file_name}")
                continue  # 跳过无法解析的文件名
            
            # 按节点编号分组文件
            if node_id not in node_files:
                node_files[node_id] = {}
            node_files[node_id][strategy] = os.path.join(results_dir, file_name)

    # 遍历节点编号，绘制每个节点的图像
    for node_id, strategies in node_files.items():
        # 创建一个大图，包含 7 个子图（每个物理量一张）
        fig, axes = plt.subplots(4, 2, figsize=(18, 24))  # 4 行 2 列布局
        fig.suptitle(f"Node {node_id} - Comparison of Strategies", fontsize=20)
        axes = axes.flatten()  # 展平子图数组

        # 初始化子图标题
        metrics = ["Qloss", "Qvoc", "Qsoc", "Qsc", "P_bat", "P_sc", "P_demand"]
        for i, metric in enumerate(metrics):
            axes[i].set_title(metric)
            axes[i].set_xlabel("Time Step")
            axes[i].set_ylabel(metric)
            axes[i].grid()

        # 遍历该节点的不同策略文件
        for strategy, file_path in strategies.items():
            # 加载数据
            data = np.load(file_path, allow_pickle=True).item()

            # 提取时间步和每个物理量的数据
            time = np.arange(len(data["Qloss"]))  # 时间步
            for i, metric in enumerate(metrics):
                axes[i].plot(time, data[metric], label=strategy)

        # 添加图例到每个子图
        for ax in axes:
            ax.legend(loc="upper right", fontsize="small")

        # 删除多余的空白子图（因4x2布局有8个子图，但只用7个）
        if len(axes) > len(metrics):
            for j in range(len(metrics), len(axes)):
                fig.delaxes(axes[j])

        # 调整布局并保存图像
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为标题留出空间
        save_path = os.path.join(save_dir, f"node_{node_id}_comparison.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved visualization for Node {node_id} to {save_path}")


if __name__ == "__main__":
    results_dir = "results"
    save_dir = "visualizations"

    # 生成对比可视化图像
    visualize_node_comparison(results_dir, save_dir=save_dir)