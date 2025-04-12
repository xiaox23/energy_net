import numpy as np
import matplotlib.pyplot as plt
from Graph_class import build_forest_graph

def extract_communication_counts(G, communication_log):
    """
    从通信日志中提取每个节点的通信次数。

    Args:
        G (networkx.Graph): 节点网络图。
        communication_log (list): 通信日志，包含路径信息。

    Returns:
        dict: 每个节点的通信次数。
    """
    # 初始化通信次数统计
    communication_count = {node: 0 for node in G.nodes}  # 每个节点的通信次数

    # 遍历通信日志
    for log in communication_log:
        path = log["path"]

        # 更新通信次数统计
        for node in path:
            communication_count[node] += 1

    return communication_count


def plot_communication_counts(communication_count, save_path=None):
    """
    绘制柱状图，显示每个节点的通信次数。

    Args:
        communication_count (dict): 每个节点的通信次数。
        save_path (str): 如果指定路径，则保存图像到文件。
    """
    # 准备数据
    nodes = list(communication_count.keys())
    counts = list(communication_count.values())

    # 创建柱状图
    x = np.arange(len(nodes))  # 节点编号作为横坐标

    plt.figure(figsize=(12, 6))
    plt.bar(x, counts, color="skyblue", width=0.6, label="Communication Count")

    # 添加标签和标题
    plt.xlabel("Node ID", fontsize=12)
    plt.ylabel("Communication Count", fontsize=12)
    plt.title("Node Communication Counts During Simulation", fontsize=16)
    plt.xticks(x, nodes)  # 设置横坐标为节点编号
    plt.legend()

    # 保存或显示图像
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Communication counts plot saved to {save_path}")
    else:
        plt.show()


# 加载通信日志
communication_log_file = "results/Battery_Only_communication_log.npy"  # 修改为你的文件路径
communication_log = np.load(communication_log_file, allow_pickle=True)

# 构建网络图
G, positions, mother_node_id = build_forest_graph(num_child_nodes=10)  # 修改节点数量

# 提取通信次数
communication_count = extract_communication_counts(G, communication_log)

# 绘制柱状图
plot_communication_counts(communication_count, save_path="communication_counts.png")