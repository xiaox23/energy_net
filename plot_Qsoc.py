import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D  # 用于自定义图例项
import os

def visualize_metric_by_strategy(results_dir, save_dir="visualizations_by_metric"):
    """
    将相同物理量的所有节点的不同策略绘制在一张图中，总共生成 7 张图。
    图例分为两部分：
    1. 每个节点的颜色，10 行。
    2. 策略的线型，2 行（黑色实线和黑色虚线表示策略）。
    """

    # 确保保存目录存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 存储每个物理量的所有节点和策略数据
    metrics = ["Qsoc"] 
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
        # plt.title(f"{metric} - Comparison Across Nodes and Strategies", fontsize=16)
        plt.xlabel("Time (d)", fontsize=32)  # 调整 x 轴字体大小
        plt.ylabel(r"$\mathit{SoC}$", fontsize=32)         # 调整 y 轴字体大小
        plt.grid()

        # 调整刻度字体大小
        plt.tick_params(axis="both", which="major", labelsize=28)  # 主刻度字体大小

        legend_handles = []  # 用于存储图例的句柄
        legend_labels = []  # 用于存储图例的标签

        # 遍历每个节点
        for node_id, strategies in sorted(all_nodes_data.items()):  # 按节点编号排序
            # 遍历该节点的所有策略
            for strategy, values in sorted(strategies.items()):  # 按策略名称排序
                # 下采样数据：每隔 60 个点显示一次
                values = values[::60]
                time_steps = len(values)
                time_days = np.arange(time_steps) * 60 / (24 * 3600)  # 转换为天，1 时间步长 = 60 秒

                # 判断策略类型及线型
                if "Voltage_Control" in strategy:
                    alpha = 1  # 电压控制策略的曲线透明度为 1
                    linestyle = "-"  # 实线
                elif "Battery_Only" in strategy:
                    alpha = 1  # 电池策略的曲线透明度为 0.7
                    linestyle = "--"  # 虚线
                else:
                    alpha = 0.5  # 默认透明度
                    linestyle = "-"  # 默认实线

                color = f"C{node_id % 10}"  # 使用 matplotlib 的颜色循环
                label = f"Node {node_id} - {strategy}"  # 图例标签

                # 绘制曲线（加粗曲线）
                plt.plot(
                    time_days, 
                    values, 
                    color=color, 
                    alpha=alpha, 
                    linestyle=linestyle, 
                    linewidth=3  # 调整曲线的粗细
                )

        # 设置 y 轴的范围
        plt.ylim(0.55, 0.85)

        # 自定义图例：节点颜色
        node_legend_handles = [
            Line2D([0], [0], color=f"C{i}", lw=2.5, label=f"Node {i}") for i in range(10)
        ]

        # 自定义图例：策略线型
        strategy_legend_handles = [
            Line2D([0], [0], color="black", lw=2.5, linestyle="-", label="Voltage Control"),
            Line2D([0], [0], color="black", lw=2.5, linestyle="--", label="Battery Only"),
        ]

        # 合并图例
        plt.legend(
            handles=node_legend_handles + strategy_legend_handles,
            loc="lower left",  # 图例位置在内部左上角
            fontsize=24,       # 图例字体大小
            ncol=2,            # 图例分为两列
            borderaxespad=1.0  # 图例与图像内容的间距
        )

        plt.tight_layout()  # 自动调整布局，避免图像和图例重叠

        # 保存图像
        save_path = os.path.join(save_dir, f"{metric}_comparison.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")  # bbox_inches="tight" 确保图像完整显示
        plt.close()
        print(f"Saved visualization for {metric} to {save_path}")


if __name__ == "__main__":
    results_dir = "paper_results/Task2_results_5d"
    save_dir = "visualizations_by_metric"

    # 生成对比可视化图像
    visualize_metric_by_strategy(results_dir, save_dir=save_dir)