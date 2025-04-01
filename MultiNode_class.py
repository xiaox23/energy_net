import numpy as np
from Node_class import simulate_node

def simulate_network_with_segmented_communication(G, node_energy_systems, num_steps, mother_node_id, En):
    """
    仿真多节点网络并通过蓝牙与母节点通信，分段计算功耗。

    Args:
        G (networkx.Graph): 网络图，表示节点之间的连接关系。
        node_energy_systems (dict): 每个子节点的能源管理系统实例。
        num_steps (int): 仿真步数。
        mother_node_id (int): 母节点的编号。
        En (array): 外部传入的太阳辐照强度数组。

    Returns:
        dict: 每个节点的仿真结果。
        list: 通信日志，记录每次通信的路径和功耗。
        dict: 节点能量消耗记录。
    """
    # 光照数据由外部提供，无需再次生成
    node_events = {
        node: np.random.choice([0, 1], size=num_steps, p=[0.8, 0.2])  # 为每个节点生成独立的事件序列
        for node in G.nodes if G.nodes[node]["role"] == "child"
    }

    results = {}
    communication_log = []  # 全局通信日志
    node_energy_consumptions = {node: 0 for node in G.nodes}  # 初始化能量消耗记录

    for node, energysystem in node_energy_systems.items():
        results[node] = simulate_node(
            energysystem=energysystem,
            num_steps=num_steps,
            En=En,  # 外部传入的光照数据
            event=node_events[node],  # 节点独立的事件序列
            G=G,
            mother_node_id=mother_node_id,
            node_energy_consumptions=node_energy_consumptions,
            node=node
        )

        # 合并通信日志
        communication_log.extend(results[node]["communication_log"])

    return results, communication_log, node_energy_consumptions