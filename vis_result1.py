import numpy as np
import matplotlib.pyplot as plt
import os

def visualize_node_results(file_path, save_dir="visualizations"):
    """
    可视化单个节点的仿真结果。
    
    Args:
        file_path (str): 节点结果文件路径。
        save_dir (str): 保存可视化图像的目录。
    """
    # 确保保存目录存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 加载结果数据
    data = np.load(file_path, allow_pickle=True).item()

    # 提取数据
    Qloss = data["Qloss"]
    Qvoc = data["Qvoc"]
    Qsoc = data["Qsoc"]
    Qi = data["Qi"]
    Qsc = data["Qsc"]
    yita_test = data["yita_test"]
    P_bat = data["P_bat"]
    P_sc = data["P_sc"]
    P_demand = data["P_demand"]

    # 绘图
    time = np.arange(len(Qloss))  # 时间步

    plt.figure(figsize=(16, 10))
    plt.subplot(3, 2, 1)
    plt.plot(time, Qloss, label="Qloss")
    plt.title("Qloss")
    plt.grid()

    plt.subplot(3, 2, 2)
    plt.plot(time, Qvoc, label="Qvoc")
    plt.title("Qvoc")
    plt.grid()

    plt.subplot(3, 2, 3)
    plt.plot(time, Qsoc, label="Qsoc")
    plt.title("Qsoc")
    plt.grid()

    plt.subplot(3, 2, 4)
    plt.plot(time, Qi, label="Qi")
    plt.title("Qi")
    plt.grid()

    plt.subplot(3, 2, 5)
    plt.plot(time, P_bat, label="P_bat")
    plt.plot(time, P_sc, label="P_sc")
    plt.plot(time, P_demand, label="P_demand")
    plt.legend()
    plt.title("Power Metrics")
    plt.grid()

    plt.subplot(3, 2, 6)
    plt.plot(time, yita_test, label="yita_test")
    plt.title("yita_test")
    plt.grid()

    # 保存图像
    file_name = os.path.basename(file_path).replace(".npy", ".png")
    save_path = os.path.join(save_dir, file_name)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved visualization to {save_path}")


if __name__ == "__main__":
    results_dir = "results"
    save_dir = "visualizations"

    # 遍历结果文件
    for file_name in os.listdir(results_dir):
        if file_name.endswith(".npy") and "node" in file_name:
            file_path = os.path.join(results_dir, file_name)
            visualize_node_results(file_path, save_dir=save_dir)