import numpy as np
import matplotlib.pyplot as plt
import os

def visualize_metric_by_strategy(results_dir, save_dir="visualizations_by_metric"):
    """
    将相同物理量的所有节点的不同策略绘制在一张图中，总共生成 7 张图。
    对电压控制策略的曲线透明度设置为 1，仅电池策略曲线透明度设置为 0.7。
    图例浮动，位于图像内部且不遮挡曲线。

    Args:
        results_dir (str): 保存仿真结果的目录。
        save_dir (str): 保存可视化图像的目录。
    """
    # 确保保存目录存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 存储每个物理量的所有节点和策略数据
    metrics = ["Qloss", "Qvoc", "Qsoc", "Qsc", "P_bat", "P_sc", "P_demand"]
    data_by_metric = {metric: {} for metric in metrics}

    # 解析结果目录中的文件名，按物理量分组数据
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
            
            # 加载数据
            file_path = os.path.join(results_dir, file_name)
            data = np.load(file_path, allow_pickle=True).item()

            # 将该节点和策略的数据分类存储
            for metric in metrics:
                if metric not in data_by_metric:
                    data_by_metric[metric] = {}
                if node_id not in data_by_metric[metric]:
                    data_by_metric[metric][node_id] = {}
                data_by_metric[metric][node_id][strategy] = data[metric]

    # 遍历每个物理量，绘制所有节点的策略数据
    for metric, all_nodes_data in data_by_metric.items():
        plt.figure(figsize=(16, 10))
        plt.title(f"{metric} - Comparison Across Nodes and Strategies", fontsize=16)
        plt.xlabel("Time (Days)", fontsize=12)
        plt.ylabel(metric, fontsize=12)
        plt.grid()

        legend_handles = []  # 用于存储图例的句柄
        legend_labels = []  # 用于存储图例的标签

        # 遍历每个节点
        for node_id, strategies in sorted(all_nodes_data.items()):  # 按节点编号排序
            # 遍历该节点的所有策略
            for strategy, values in sorted(strategies.items()):  # 按策略名称排序
                time_steps = len(values)
                time_days = np.arange(time_steps) / (24 * 3600)  # 转换时间步为天（假设 1 秒时间步长）

                # 判断策略类型
                if "Voltage_Control" in strategy:
                    alpha = 1  # 电压控制策略的曲线透明度为 1
                elif "Battery_Only" in strategy:
                    alpha = 0.3  # 电池策略的曲线透明度为 0.3
                else:
                    alpha = 0.5  # 默认透明度（其他策略）

                color = f"C{node_id % 10}"  # 使用 matplotlib 的颜色循环
                label = f"Node {node_id} - {strategy}"  # 图例标签

                # 绘制曲线
                line, = plt.plot(time_days, values, color=color, alpha=alpha)
                if alpha > 0 and label not in legend_labels:  # 只添加显示的曲线到图例
                    legend_handles.append(line)
                    legend_labels.append(label)

        # 添加浮动图例，位于图像内部右上方
        plt.legend(
            legend_handles, legend_labels, 
            loc="upper right",  # 图例位置在内部右上角
            fontsize="small", ncol=1,  # 图例列数为 1
            borderaxespad=1.0  # 图例与图像内容的间距
        )

        plt.tight_layout()  # 自动调整布局，避免图像和图例重叠

        # 保存图像
        save_path = os.path.join(save_dir, f"{metric}_comparison.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")  # bbox_inches="tight" 确保图像完整显示
        plt.close()
        print(f"Saved visualization for {metric} to {save_path}")


if __name__ == "__main__":
    results_dir = "results"
    save_dir = "visualizations_by_metric"

    # 生成对比可视化图像
    visualize_metric_by_strategy(results_dir, save_dir=save_dir)