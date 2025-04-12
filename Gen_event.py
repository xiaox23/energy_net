import numpy as np
import matplotlib.pyplot as plt
import os

def ensure_directory_exists(directory):
    """
    确保指定的目录存在，如果不存在则创建。

    Args:
        directory (str): 目录路径。
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_event_series(dt, simulation_days, n, output_file_template="event/event_series_n{}_dt{}_days{}_seed{}.npy", seed=42):
    """
    生成事件数列并保存为 .npy 文件。

    Args:
        dt (int): 时间步长，单位为秒。
        simulation_days (int): 仿真天数。
        n (int): 节点数量。
        output_file_template (str): 输出文件名模板，默认为 "event/event_series_n{}_dt{}_days{}_seed{}.npy"。
        seed (int): 随机数种子，用于可重复性。

    Returns:
        np.ndarray: 生成的事件数列，形状为 [n, steps]。
        str: 保存的文件名。
    """
    # 确保文件夹存在
    ensure_directory_exists(os.path.dirname(output_file_template))

    # 设置随机数种子以保证可重复性
    if seed is not None:
        np.random.seed(seed)

    # 计算仿真总步数
    steps_per_day = int(24 * 60 * 60 / dt)  # 一天的步数
    total_steps = steps_per_day * simulation_days  # 总步数

    # 随机生成 [n, total_steps] 的事件数列 (0 或 1)
    event_series = np.random.choice([0, 1], size=(n, total_steps), p=[0.8, 0.2])

    # 动态生成文件名，包含 seed 信息
    output_file = output_file_template.format(n, dt, simulation_days, seed)

    # 将事件数列保存到 .npy 文件
    np.save(output_file, event_series)

    return event_series, output_file

def plot_event_series(event_series, dt, simulation_days, n, output_image_template="event/event_series_plot_n{}_dt{}_days{}_seed{}.png"):
    """
    绘制事件数列柱状图并保存为图像。

    Args:
        event_series (np.ndarray): 事件数列，形状为 [n, steps]。
        dt (int): 时间步长，单位为秒。
        simulation_days (int): 仿真天数。
        n (int): 节点数量。
        output_image_template (str): 输出的图像文件名模板，默认为 "event/event_series_plot_n{}_dt{}_days{}.png"。
    """
    # 确保文件夹存在
    ensure_directory_exists(os.path.dirname(output_image_template))

    # 获取时间序列
    n, steps = event_series.shape
    time = np.arange(0, steps * dt, dt) / 3600  # 转换为小时

    # 动态生成图像文件名
    output_image = output_image_template.format(n, dt, simulation_days)

    # 创建纵向排列的子图
    fig, axes = plt.subplots(n, 1, figsize=(12, 3 * n), sharex=True, constrained_layout=True)

    # 遍历每个节点，绘制柱状图
    for i in range(n):
        axes[i].bar(time, event_series[i], width=(dt / 3600) * 0.8, color="skyblue", edgecolor="skyblue", align="center")
        axes[i].set_ylabel(f"Node {i + 1}")
        axes[i].set_ylim(0, 1.2)  # 限制 y 轴范围
        axes[i].grid(True, linestyle="--", alpha=0.6)

    # 设置共享的 x 轴标签和标题
    axes[-1].set_xlabel("Time (hours)")
    # fig.suptitle("Event Series for Nodes (Bar Plots)", fontsize=16)

    # 保存图像
    plt.savefig(output_image, dpi=300)
    plt.close()

    return output_image

if __name__ == "__main__":
    # 参数设置
    dt = 1  # 时间步长5分钟 [s]
    simulation_days = 5  # 仿真天数
    simulation_days = 30  # 仿真天数
    n = 10  # 节点数量
    seed = 5  # 设置随机数种子以保证可重复性

    # 调用函数生成事件数列
    event_series, event_series_file = generate_event_series(
        dt, simulation_days, n, seed=seed
    )

    # 输出结果
    print("事件数列的形状:", event_series.shape)
    print(f"事件数列已保存为 '{event_series_file}'")

    # # 绘制并保存事件发生柱状图
    # event_series_plot_file = plot_event_series(
    #     event_series, dt, simulation_days, n, output_image_template="event/event_series_plot_n{}_dt{}_days{}.png"
    # )
    # print(f"事件数列柱状图已保存为 '{event_series_plot_file}'")