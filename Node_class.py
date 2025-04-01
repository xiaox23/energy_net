import numpy as np
from comp import Sensor, SuperCapacitor, LiBattery, SolarHarvester, Energysystem  # 导入元件类
import matplotlib.pyplot as plt
import networkx as nx
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

def simulate_node(energysystem, num_steps, En, event, G, mother_node_id, node_energy_consumptions, node):
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
        node_energy_consumptions (dict): 记录每个节点的能量消耗。
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
    switch_count = 0
    last_energy_source = None
    communication_log = []

    for step in range(num_steps):
        sun = En[step]
        event_state = event[step]

        # 更新能源系统状态
        output = energysystem.update(event_state, sun)
        if output is None:
            break

        # 记录能量消耗
        energy_consumed += energysystem.P_demand * energysystem.dt

        # 记录能源切换次数
        current_energy_source = "battery" if energysystem.P_batt > 0 else "supercapacitor"
        if last_energy_source is not None and current_energy_source != last_energy_source:
            switch_count += 1
        last_energy_source = current_energy_source

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
        if event_state == 1:
            # print(f"Event triggered at step {step}. Initiating communication with Mother Node.")
            path, total_cost, node_energy_consumptions = communicate_with_mother(
                G, source_node=node,  # 使用传入的节点 ID
                mother_node_id=mother_node_id,
                node_energy_consumptions=node_energy_consumptions
            )
            if path:
                # print(f"Communication successful. Path: {path}, Cost: {total_cost}")
                communication_log.append({
                    "step": step,
                    "path": path,
                    "total_cost": total_cost,
                })
                communication_power = total_cost / energysystem.dt
                bluetooth_energy_consumed += total_cost  # 累积蓝牙通信的能耗
                energysystem.P_demand += communication_power

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
        "switch_count": switch_count,
        "bluetooth_energy_consumed": bluetooth_energy_consumed,  # 蓝牙通信能耗
        "communication_log": communication_log,
    }



def communicate_with_mother(G, source_node, mother_node_id, node_energy_consumptions):
    """
    使用 Dijkstra 最短路径算法从子节点通过蓝牙与母节点通信，
    并将每段通信功耗分配给发出信号的节点。
    
    Args:
        G (networkx.Graph): 网络图。
        source_node (int): 触发事件的子节点 ID。
        mother_node_id (int): 母节点 ID。
        node_energy_consumptions (dict): 记录每个节点的能量消耗。

    Returns:
        path (list): 最短路径上的节点列表。
        total_cost (float): 通信总功耗（基于边权重）。
        updated_energy (dict): 更新后的节点能量消耗记录。
    """
    try:
        # 使用 Dijkstra 算法计算最短路径
        path = nx.dijkstra_path(G, source=source_node, target=mother_node_id, weight="weight")
        total_cost = 0  # 初始化总功耗

        # 遍历路径的每一段，计算功耗并分配给当前节点
        for i in range(len(path) - 1):
            # 当前段的起点和终点
            current_node = path[i]
            next_node = path[i + 1]

            # 当前段的通信功耗（边权重）
            segment_cost = G.edges[current_node, next_node]["weight"]

            # 将功耗累加到当前节点的能耗记录中
            node_energy_consumptions[current_node] += segment_cost

            # 累计总功耗
            total_cost += segment_cost

        return path, total_cost, node_energy_consumptions
    except nx.NetworkXNoPath:
        # 如果没有路径可达
        # print(f"Node {source_node} cannot communicate with Mother Node {mother_node_id}")
        return [], float("inf"), node_energy_consumptions