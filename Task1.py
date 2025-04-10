import numpy as np
from Node_class import initialize_node_energy_system
from Graph_class import build_forest_graph
from MultiNode_class import simulate_network_with_segmented_communication
from Gen_sun import solar_irradiance
from tqdm import tqdm

# ================================
# 1. 仿真参数设置
# ================================
Tp = 10   # 传感器周期时间 [s]
Ta = 2    # 活动时间 [s]
Ps = 10   # 休眠功耗 [mW]
Pa = 20   # 活动功耗 [mW]
Ph = 100  # 高负载功耗 [mW]
Q = 3   # 电池容量 [Ah]
S_s = 60  # 太阳能板面积 [cm^2]
dt = 1  # 时间步长 [s]
simulation_days = 5  # 仿真天数
num_steps = int(simulation_days * 24 * 3600 / dt)  # 仿真步数
num_child_nodes = 10  # 子节点数量

# 生成统一的太阳辐照强度数据
En = np.zeros(num_steps)  # 预分配数组
for step in tqdm(range(num_steps), desc="Generating Solar Data", unit="step"):  # 添加进度条
    hour = (step * dt) / 3600 % 24  # 当前时间（小时），取余 24 小时
    En[step] = solar_irradiance(hour, Im=1000)  # 计算每个时间步的太阳辐照强度


# ================================
# 2. 构建多节点网络
# ================================
G, positions, mother_node_id = build_forest_graph(num_child_nodes=num_child_nodes)

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


# ================================
# 3. 运行仿真并记录结果
# ================================


def run_simulation_and_save_results(node_energy_systems, strategy_name, event_file):
    # 调用仿真函数
    results, communication_log, node_energy_consumptions = simulate_network_with_segmented_communication(
        G, node_energy_systems, num_steps, mother_node_id, En, event_file
    )

    # 输出仿真结果
    total_runtime = sum(result["runtime"] for result in results.values())
    print(f"Total runtime for strategy {strategy_name}: {total_runtime:.2f} seconds")


# 指定事件文件路径
event_file = "event/event_series_n10_dt1_days5.npy"

# 运行策略1（仅电池）和策略3（电压控制）的仿真，并保存结果
run_simulation_and_save_results(node_energy_systems_1, "Battery_Only", event_file)
run_simulation_and_save_results(node_energy_systems_3, "Voltage_Control", event_file)


print("=================  Finished!  ===================")