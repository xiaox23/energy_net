import numpy as np
from comp import Sensor, SuperCapacitor, LiBattery, SolarHarvester, Energysystem  # 导入元件类
import matplotlib.pyplot as plt
import networkx as nx
from tqdm import tqdm
# ================================
# 1. 初始化节点能源系统
# ================================

def initialize_node_energy_system(Tp, Ta, Ps, Pa, Ph, Q, S_s, dt, management_strategy):
    """
    初始化单个节点的能源系统
    """
    # 初始化各个元件
    sensor = Sensor(Tp, Ta, Ps, Pa, Ph)
    SC = SuperCapacitor()
    battery = LiBattery(A0=Q)
    solar_harvester = SolarHarvester(Area=S_s)

    # 初始化能源系统
    energysystem = Energysystem(
        dt=dt,
        sensor=sensor,
        supercapacitor=SC,
        battery=battery,
        solar_harvester=solar_harvester,
        Ps_a=((Ps * (Tp - Ta) + Pa * Ta) / Tp),
        management=management_strategy,
        k=[2, 0.64, 3.4, -0.7, 0]  # 策略参数
    )
    return energysystem

# ================================
# 2. 仿真功能
# ================================

def simulate_node(energysystem, num_steps, En, event, G, mother_node_id, node, node_energy_systems):
    """
    仿真单节点运行，并记录各类状态变量。
    当某个时间步发生事件时，子节点与母节点通过网络通信。

    Args:
        energysystem (Energysystem): 节点的能源管理系统实例。
        num_steps (int): 仿真步数。
        En (array): 太阳辐照强度数组（每个时间步的 W/m²）。
        event (array): 事件状态数组（每个时间步的状态，0 表示正常，1 表示高负载事件）。
        G (networkx.Graph): 网络图，表示节点之间的连接关系。
        mother_node_id (int): 母节点的编号。
        node (int): 当前节点的 ID。

    Returns:
        dict: 包含以下记录的字典。
    """
    # 初始化记录变量
    Qloss = np.zeros(num_steps)
    Qvoc = np.zeros(num_steps)
    Qsoc = np.zeros(num_steps)
    Qi = np.zeros(num_steps)
    Qsc = np.zeros(num_steps)
    yita_test = np.ones(num_steps)
    P_bat = np.zeros(num_steps)
    P_sc = np.zeros(num_steps)
    P_demand = np.zeros(num_steps)

    energy_consumed = 0
    communication_log = []

    for step in tqdm(range(num_steps),desc=f'simulate_node_{node}'):
        sun = En[step]
        event_state = event[step]

        # 更新能源系统状态
        output = energysystem.update(event_state, sun)
        if output is None:
            break

        # 记录能量消耗
        energy_consumed += energysystem.P_demand * energysystem.dt

        # 提前结束条件
        if energysystem.battery.Qloss > 0.45:
            # print(f"Simulation terminated early at step {step}, time {step * energysystem.dt:.2f} seconds")
            break

        # 记录状态变量
        Qloss[step] = energysystem.battery.Qloss - 0.01
        Qvoc[step] = energysystem.battery.Voc
        Qsoc[step] = energysystem.battery.Soc
        Qi[step] = energysystem.battery.I
        Qsc[step] = energysystem.supercapacitor.Soc
        yita_test[step] = energysystem.yita
        P_bat[step] = energysystem.P_batt
        P_sc[step] = energysystem.P_sc
        P_demand[step] = energysystem.P_demand

        bluetooth_energy_consumed = 0  # 初始化蓝牙通信能耗
        # 当事件发生时，与母节点通信
        # 处理通信逻辑时，可以访问 node_energy_systems
        if event_state == 1:
            path, total_cost = communicate_with_mother(
                G, source_node=node,
                mother_node_id=mother_node_id,
                node_energy_systems=node_energy_systems,  # 使用 node_energy_systems
                dt=energysystem.dt,
            )
            # 记录通信日志
            if path:
                communication_log.append({
                    "step": step,
                    "path": path,
                    "total_cost": total_cost,
                })

    runtime = step * energysystem.dt

    return {
        "Qloss": Qloss[:step],
        "Qvoc": Qvoc[:step],
        "Qsoc": Qsoc[:step],
        "Qi": Qi[:step],
        "Qsc": Qsc[:step],
        "yita_test": yita_test[:step],
        "P_bat": P_bat[:step],
        "P_sc": P_sc[:step],
        "P_demand": P_demand[:step],
        "runtime": runtime,
        "energy_consumed": energy_consumed,
        "bluetooth_energy_consumed": bluetooth_energy_consumed,  # 蓝牙通信能耗
        "communication_log": communication_log,
    }



def communicate_with_mother(G, source_node, mother_node_id, node_energy_systems, dt):
    """
    使用 Dijkstra 最短路径算法从子节点通过蓝牙与母节点通信，
    并将每段通信功耗分配给路径上的前一个节点，并更新其能源系统。

    Args:
        G (networkx.Graph): 网络图。
        source_node (int): 触发事件的子节点 ID。
        mother_node_id (int): 母节点 ID。
        node_energy_systems (dict): 每个子节点的能源管理系统实例。
        dt (float): 时间步长。

    Returns:
        path (list): 最短路径上的节点列表。
        total_cost (float): 通信总功耗（基于边权重）。
    """
    try:
        # 使用 Dijkstra 算法计算最短路径
        path = nx.dijkstra_path(G, source=source_node, target=mother_node_id, weight="weight")
        total_cost = 0  # 初始化总功耗

        # 遍历路径的每一段，计算功耗并更新前一个节点的能源系统
        for i in range(len(path) - 1):
            current_node = path[i]  # 当前节点
            next_node = path[i + 1]  # 下一个节点

            # 获取当前段的通信功耗（边权重）
            segment_cost = G.edges[current_node, next_node]["weight"]

            # 累计总功耗
            total_cost += segment_cost

            # 更新当前节点的能源系统，承担这一段通信的功耗
            if current_node in node_energy_systems:
                node_energy_systems[current_node].update(0, -segment_cost)

        return path, total_cost
    except nx.NetworkXNoPath:
        # 如果没有路径可达
        return [], float("inf")