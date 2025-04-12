import numpy as np
from Node_class import simulate_node
from joblib import Parallel, delayed

def simulate_network_with_segmented_communication(G, node_energy_systems, num_steps, mother_node_id, En, event_file):
    """
    仿真多节点网络并通过蓝牙与母节点通信，分段计算功耗。

    Returns:
        dict: 每个节点的仿真结果（包含所有时间步的物理量）。
        list: 通信日志，记录每次通信的路径和功耗。
        dict: 节点能量消耗记录。
    """
    all_events = np.load(event_file)  # 加载事件矩阵

    results = {}
    communication_log = []  # 全局通信日志

    def fun(node, energysystem):
        event = all_events[node]  # 获取当前节点的事件序列
        results[node] = simulate_node(
            energysystem=energysystem,
            num_steps=num_steps,
            En=En,
            event=event,
            G=G,
            mother_node_id=mother_node_id,
            node=node,
            node_energy_systems=node_energy_systems,
        )
        communication_log.extend(results[node]["communication_log"])

    n_jobs = len(node_energy_systems)
    Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(fun)(node, energysystem) for (node, energysystem) in node_energy_systems.items()
    )

    return results, communication_log, {}