import numpy as np
import matplotlib.pyplot as plt
from Node_class import initialize_node_energy_system
from Graph_class import build_forest_graph, visualize_graph
from MultiNode_class import simulate_network_with_segmented_communication

# ================================
# 新增太阳辐照强度函数
# ================================
def solar_irradiance(h, Im):
    """
    计算太阳辐照强度（W/m^2）。
    h: 当前时间（小时，允许小数，范围 0-24）。
    Im: 最大太阳辐照强度（W/m^2）。
    """
    StartHour = 6  # 日出时间
    EndHour = 18   # 日落时间
    if StartHour < h < EndHour:
        # 太阳辐照强度的正弦分布
        Irradiance = Im * (1 + np.cos(2 * np.pi / (EndHour - StartHour) * (h - 12))) / 2
    else:
        Irradiance = 0
    return Irradiance

# ================================
# 1. 仿真参数设置
# ================================
Tp = 10   # 传感器周期时间 [s]
Ta = 2    # 活动时间 [s]
Ps = 10   # 休眠功耗 [mW]
Pa = 20   # 活动功耗 [mW]
Ph = 200  # 高负载功耗 [mW]
Q = 0.3   # 电池容量 [Ah]
S_s = 40  # 太阳能板面积 [cm^2]
dt = 1  # 时间步长 [s]
simulation_days = 20  # 仿真天数
# simulation_days = 0.03125  # 仿真天数
num_steps = int(simulation_days * 24 * 3600 / dt)  # 仿真步数
num_child_nodes = 5  # 子节点数量

# ================================
# 2. 构建多节点网络
# ================================
G, positions, mother_node_id = build_forest_graph(num_child_nodes=num_child_nodes, forest_radius=500, min_neighbors=1)

# 为每个子节点分配能源管理策略
node_energy_systems_1 = {}  # 策略1（仅电池）
node_energy_systems_3 = {}  # 策略3（电压控制）

for node in G.nodes:
    if G.nodes[node]["role"] == "child":  # 仅为子节点分配能源系统
        node_energy_systems_1[node] = initialize_node_energy_system(
            Tp=Tp, Ta=Ta, Ps=Ps, Pa=Pa, Ph=Ph, Q=Q, S_s=S_s, dt=dt, management_strategy=1
        )
        node_energy_systems_3[node] = initialize_node_energy_system(
            Tp=Tp, Ta=Ta, Ps=Ps, Pa=Pa, Ph=Ph, Q=Q, S_s=S_s, dt=dt, management_strategy=3
        )

# 可视化网络结构
visualize_graph(G, positions, mother_node_id)

# ================================
# 3. 运行仿真并记录结果
# ================================
from tqdm import tqdm  # 导入 tqdm 库

def run_simulation_and_save_results(node_energy_systems, strategy_name):
    # 生成统一的太阳辐照强度数据
    En = np.zeros(num_steps)
    # print(f"Generating solar irradiance data for strategy: {strategy_name}")
    for step in tqdm(range(num_steps), desc="Generating Solar Data", unit="step"):  # 添加进度条
        hour = (step * dt) / 3600 % 24  # 当前时间（小时）
        En[step] = solar_irradiance(hour, Im=1000)  # 最大太阳辐照强度为 1000 W/m^2

    # 将光照数据传递给仿真函数
    # print(f"Simulating network for strategy: {strategy_name}")
    results, communication_log, node_energy_consumptions = simulate_network_with_segmented_communication(
        G, node_energy_systems, num_steps, mother_node_id, En
    )

    # 绘制太阳辐照强度曲线
    time = np.arange(num_steps) * dt / 3600  # 转换为小时
    plt.figure(figsize=(12, 6))
    plt.plot(time, En, label="Solar Irradiance (W/m²)", color="orange")
    plt.xlabel("Time (hours)")
    plt.ylabel("Solar Irradiance (W/m²)")
    plt.title(f"Solar Irradiance Over Time ({strategy_name})")
    plt.grid()
    plt.legend()
    plt.savefig(f"Solar_Irradiance_{strategy_name}.svg", format="svg")
    plt.close()

    # 保存每个节点的物理量和事件数据随时间变化的曲线
    # print(f"Saving simulation results for strategy: {strategy_name}")
    for node_id, result in tqdm(results.items(), desc="Processing Nodes", unit="node"):
        time = np.arange(len(result["Qloss"])) * dt  # 时间轴

        # 绘制并保存电池 SOC 曲线
        plt.figure()
        plt.plot(time, result["Qsoc"], label="Battery SOC", color="blue")
        plt.xlabel("Time (s)")
        plt.ylabel("SOC")
        plt.title(f"Node {node_id} Battery SOC ({strategy_name})")
        plt.grid()
        plt.legend()
        plt.savefig(f"Node_{node_id}_Battery_SOC_{strategy_name}.svg", format="svg")
        plt.close()

        # 绘制并保存超级电容 SOC 曲线
        plt.figure()
        plt.plot(time, result["Qsc"], label="Supercapacitor SOC", color="green")
        plt.xlabel("Time (s)")
        plt.ylabel("SOC")
        plt.title(f"Node {node_id} Supercapacitor SOC ({strategy_name})")
        plt.grid()
        plt.legend()
        plt.savefig(f"Node_{node_id}_Supercapacitor_SOC_{strategy_name}.svg", format="svg")
        plt.close()

        # 绘制并保存电池容量损失 Qloss 曲线
        plt.figure()
        plt.plot(time, result["Qloss"], label="Battery Capacity Loss (Qloss)", color="red")
        plt.xlabel("Time (s)")
        plt.ylabel("Qloss")
        plt.title(f"Node {node_id} Battery Capacity Loss ({strategy_name})")
        plt.grid()
        plt.legend()
        plt.savefig(f"Node_{node_id}_Battery_Qloss_{strategy_name}.svg", format="svg")
        plt.close()

    # 计算系统总工作时长
    total_runtime = sum(result["runtime"] for result in results.values())
    # print(f"Total runtime for strategy {strategy_name}: {total_runtime:.2f} seconds")


# 运行策略1（仅电池）和策略3（电压控制）的仿真，并保存结果
run_simulation_and_save_results(node_energy_systems_1, "Battery_Only")
run_simulation_and_save_results(node_energy_systems_3, "Voltage_Control")
