import numpy as np
from Node_class import simulate_node
from joblib import Parallel, delayed

def simulate_network_with_segmented_communication(G, node_energy_systems, num_steps, mother_node_id, En, event_file):
    """
    仿真多节点网络并通过蓝牙与母节点通信，分段计算功耗。

    Args:
        G (networkx.Graph): 网络图，表示节点之间的连接关系。
        node_energy_systems (dict): 每个子节点的能源管理系统实例。
        num_steps (int): 仿真步数。
        mother_node_id (int): 母节点的编号。
        En (array): 外部传入的太阳辐照强度数组。
        event_file (str): 包含所有节点事件数列的 .npy 文件路径。

    Returns:
        dict: 每个节点的仿真结果。
        list: 通信日志，记录每次通信的路径和功耗。
        dict: 节点能量消耗记录。
    """
    # 从单个 .npy 文件加载事件矩阵
    all_events = np.load(event_file)  # 事件矩阵，形状为 (n, steps)

    # 检查事件矩阵的形状是否与网络和仿真参数匹配
    num_nodes, total_steps = all_events.shape
    if total_steps != num_steps:
        raise ValueError(f"事件矩阵的时间步数 ({total_steps}) 与仿真步数 ({num_steps}) 不匹配！")
    if len(node_energy_systems) != num_nodes:
        raise ValueError(f"节点数量 ({len(node_energy_systems)}) 与事件矩阵的行数 ({num_nodes}) 不匹配！")

    results = {}
    communication_log = []  # 全局通信日志
    node_energy_consumptions = {node: 0 for node in G.nodes}  # 初始化能量消耗记录

    def fun(node, energysystem):
        # 提取当前节点的事件数列
        event = all_events[node]  # 从事件矩阵中取出对应行
        results[node] = simulate_node(
            energysystem=energysystem,
            num_steps=num_steps,
            En=En,
            event=event,  # 使用提取的事件数列
            G=G,
            mother_node_id=mother_node_id,
            node=node,
            node_energy_systems=node_energy_systems,
        )
        communication_log.extend(results[node]["communication_log"])

    # 动态设置并行线程数，等于节点的个数
    n_jobs = len(node_energy_systems)
    Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(fun)(node, energysystem) for (node, energysystem) in node_energy_systems.items()
    )

    return results, communication_log, node_energy_consumptions