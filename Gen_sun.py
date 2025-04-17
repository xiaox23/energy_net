import numpy as np
import random
import matplotlib.pyplot as plt

# 太阳辐照函数（加入云遮挡概率作为参数）
def solar_irradiance(h, Im, cloud_probability=0.1):
    """
    计算太阳辐照强度（W/m^2），同时考虑阴云遮挡的影响。
    
    参数：
    h: 当前时间（小时，允许小数，范围 0-24）。
    Im: 最大太阳辐照强度（W/m^2）。
    cloud_probability: 阴云遮挡的概率（范围 0-1，默认值为 0.1）。
    
    返回：
    太阳辐照强度（W/m^2）。
    """
    StartHour = 6  # 日出时间
    EndHour = 18   # 日落时间
    
    # 模拟阴云遮挡的 cloud_probability 概率
    np.random.seed(25)
    cloud_blocked = random.random() < cloud_probability

    if StartHour < h < EndHour and not cloud_blocked:
        # 太阳辐照强度的正弦分布
        Irradiance = Im * (1 + np.cos(2 * np.pi / (EndHour - StartHour) * (h - 12))) / 2
    else:
        Irradiance = 0  # 阴云遮挡或没有太阳光时的辐照强度为 0

    return Irradiance

if __name__ == "__main__":
    # 仿真设置
    Im = 1000  # 最大太阳辐照强度（W/m^2）
    cloud_probability = 0.1  # 阴云遮挡概率
    simulation_step = 5 / 60  # 仿真步长（小时），5分钟=5/60小时
    simulation_hours = np.arange(0, 24, simulation_step)  # 从0到24小时，每步长1分钟

    # 计算每分钟的太阳辐照强度
    irradiance_values = [solar_irradiance(h, Im, cloud_probability) for h in simulation_hours]

    # 绘制柱状图
    plt.figure(figsize=(14, 6))  # 设置图像尺寸
    plt.bar(simulation_hours, irradiance_values, color="orange", edgecolor="orange", alpha=0.7, width=1/60)

    # 设置标题和轴标签
    # plt.title("Solar Irradiance Over the Day (5-Minute Interval)", fontsize=16)
    plt.xlabel("Time (Hour)", fontsize=12)
    plt.ylabel("Solar Irradiance (W/m^2)", fontsize=12)

    # 设置横坐标显示为整点小时
    plt.xticks(np.arange(0, 25, 1))  # 每隔 1 小时显示一个刻度，并覆盖到 24 小时
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    # 保存高清图像
    plt.savefig("solar_irradiance_simulation_hd.png", dpi=600, bbox_inches="tight")

    # 显示图像
    plt.show()