import numpy as np
from Node_class import simulate_node
from joblib import Parallel, delayed

def simulate_network_with_segmented_communication(G, node_energy_systems, num_steps, mother_node_id, En, events):
    """
    仿真多节点网络并通过蓝牙与母节点通信，分段计算功耗。

    Args:
        G (networkx.Graph): 网络图，表示节点之间的连接关系。
        node_energy_systems (dict): 每个子节点的能源管理系统实例。
        num_steps (int): 仿真步数。
        mother_node_id (int): 母节点的编号。
        En (array): 外部传入的太阳辐照强度数组。
        events (dict): 外部生成的事件序列，每个子节点对应一个事件数列。

    Returns:
        dict: 每个节点的仿真结果。
        list: 通信日志，记录每次通信的路径和功耗。
        dict: 节点能量消耗记录。
    """
    # 检查传入的事件序列是否完整
    if not all(node in events for node in G.nodes if G.nodes[node]["role"] == "child"):
        raise ValueError("所有子节点都必须有对应的事件序列")

    results = {}
    communication_log = []  # 全局通信日志
    node_energy_consumptions = {node: 0 for node in G.nodes}  # 初始化能量消耗记录

    def fun(node, energysystem):
        results[node] = simulate_node(
            energysystem=energysystem,
            num_steps=num_steps,
            En=En,
            event=events[node],  # 使用外部传入的事件序列
            G=G,
            mother_node_id=mother_node_id,
            node_energy_consumptions=node_energy_consumptions,
            node=node,
            node_energy_systems=node_energy_systems,  # 添加参数
        )
        communication_log.extend(results[node]["communication_log"])

    # 动态设置并行线程数，等于节点的个数
    n_jobs = len(node_energy_systems)  # 子节点数量
    Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(fun)(node, energysystem) for (node, energysystem) in node_energy_systems.items()
    )
    assert len(communication_log)

    return results, communication_log, node_energy_consumptions