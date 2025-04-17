import os
import re
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# 定义存储数据的结构
data = {
    "Battery_Only": [],
    "Voltage_Control": []
}

# 文件夹路径
base_folder = "paper_results"

# 遍历所有文件夹和文件
for root, dirs, files in os.walk(base_folder):  # 使用 os.walk 遍历所有子文件夹
    # 限制文件夹名称必须包含 "Task3_results_30d"
    if "Task3_results_30d" in root:
        for file_name in files:
            if file_name == "simulation_metrics.txt":  # 查找 simulation_metrics.txt 文件
                file_path = os.path.join(root, file_name)
                # 提取 ph 值
                ph_match = re.search(r"_ph(\d+)", root)
                if ph_match:
                    ph = int(ph_match.group(1))
                    # 读取文件内容
                    with open(file_path, "r") as f:
                        lines = f.readlines()
                        current_strategy = None
                        avg_node_lifetime = None
                        node_failure_rate = None
                        for line in lines:
                            if "Strategy:" in line:
                                current_strategy = line.split(":")[-1].strip()
                            elif "Average Node Lifetime" in line:
                                avg_node_lifetime = float(line.split(":")[-1].strip().split()[0])  # 提取数值
                            elif "Node Failure Rate" in line:
                                node_failure_rate = float(line.split(":")[-1].strip().replace("%", ""))  # 转换为数值

                            # 如果当前策略的数据已经完整，保存并重置
                            if current_strategy and avg_node_lifetime is not None and node_failure_rate is not None:
                                data[current_strategy].append({
                                    "ph": ph,
                                    "avg_node_lifetime": avg_node_lifetime,
                                    "node_failure_rate": node_failure_rate
                                })
                                avg_node_lifetime = None
                                node_failure_rate = None

# 按 ph 值排序数据
for strategy in data:
    data[strategy] = sorted(data[strategy], key=lambda x: x["ph"])

# 打印原始数据
print("Original Data for Plotting:")
for strategy, strategy_data in data.items():
    print(f"\nStrategy: {strategy}")
    print(f"{'Ph':<10}{'Avg Node Lifetime':<20}{'Node Failure Rate (%)':<20}")
    for item in strategy_data:
        print(f"{item['ph']:<10}{item['avg_node_lifetime']:<20}{item['node_failure_rate']:<20}")

# 准备绘图数据
fig, ax1 = plt.subplots(figsize=(16, 9))

# 设置全局字体大小
plt.rcParams.update({'font.size': 16})

# 定义新的样式
styles = {
    "Battery_Only": {
        "avg_lifetime": {"color": "tab:green", "marker": "o", "linestyle": "--"},
        "failure_rate": {"color": "tab:blue", "marker": "o", "linestyle": "--"}
    },
    "Voltage_Control": {
        "avg_lifetime": {"color": "tab:green", "marker": "o", "linestyle": "-"},
        "failure_rate": {"color": "tab:blue", "marker": "o", "linestyle": "-"}
    }
}

# 创建双 y 轴
ax2 = ax1.twinx()

# 绘制曲线
for strategy, strategy_data in data.items():
    ph_values = [item["ph"] for item in strategy_data]
    avg_node_lifetimes = [item["avg_node_lifetime"] for item in strategy_data]
    node_failure_rates = [item["node_failure_rate"] for item in strategy_data]

    # 左 y 轴: Average Node Lifetime
    ax1.plot(ph_values, avg_node_lifetimes,
             label=f"{strategy} - Avg Lifetime",
             **styles[strategy]["avg_lifetime"], linewidth=2.5, markersize=12)

    # 右 y 轴: Node Failure Rate
    ax2.plot(ph_values, node_failure_rates,
             label=f"{strategy} - Failure Rate",
             **styles[strategy]["failure_rate"], linewidth=2.5, markersize=12)

# 设置轴标签和标题
ax1.set_xlabel(r"$P_{\mathrm{h}}$", fontsize=32)
ax1.set_ylabel("Average Node Lifetime (d)", fontsize=32, color="tab:green")  # 左 y 轴标签颜色
ax2.set_ylabel("Node Failure Rate (%)", fontsize=32, color="tab:blue")  # 右 y 轴标签颜色

# 调整坐标刻度字体大小与颜色
ax1.tick_params(axis='y', labelsize=28, colors="tab:green")  # 左 y 轴刻度颜色
ax2.tick_params(axis='y', labelsize=28, colors="tab:blue")  # 右 y 轴刻度颜色
ax1.tick_params(axis='x', labelsize=28)  # x 轴刻度颜色保持默认

# 自定义图例
custom_legend = [
    Line2D([0], [0], color="black", linestyle="-", linewidth=2.5, label="Voltage_Control"),
    Line2D([0], [0], color="black", linestyle="--", linewidth=2.5, label="Battery_Only")
]

# 添加自定义图例
ax1.legend(
    handles=custom_legend,
    loc="center left",           # 图例框的左侧中心为锚点
    bbox_to_anchor=(0.05, 0.7),  #锚点放在图表左侧的中间，-0.2 是向左偏移的距离
    fontsize=24,                 # 设置字体大小
    frameon=True                 # 图例框可见
)

# 调整图表边距，避免重叠
fig.subplots_adjust(left=0.15, right=0.85)

# 使用 align_ylabels 对齐双 y 轴标签
fig.align_ylabels([ax1, ax2])

# 保存图片到文件
plt.savefig("simulation_metrics.png", dpi=300, bbox_inches="tight")

# 显示图表
plt.tight_layout()
plt.show()