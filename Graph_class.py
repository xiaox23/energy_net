import networkx as nx
import random
import math
import matplotlib.pyplot as plt

def build_forest_graph(num_child_nodes=10, forest_radius=500, min_neighbors=1, bluetooth_range=100, initial_energy=100, seed=81):
    """
    构建一个包含随机分布的子节点和中央母节点的无向图。
    母节点位于森林中央，子节点随机分布在森林范围内，且每个子节点的半径范围内有
    至少指定数量的其他节点。
    同时确保母节点周围至少有一个距离小于 bluetooth_range 的子节点。

    Args:
        num_child_nodes (int): 子节点的数量。
        forest_radius (float): 森林的半径范围（圆形区域）。
        min_neighbors (int): 每个子节点半径范围内至少的其他节点数量。
        bluetooth_range (float): 蓝牙通信范围（单位：米）。
        initial_energy (float): 子节点的初始能量（单位：J 或其他能量单位）。
        seed (int): 随机数生成器的种子值。

    Returns:
        G (networkx.Graph): 构建的无向图。
        positions (dict): 节点位置，用于可视化。
        mother_node_id (int): 母节点的编号。
    """
    # 设置随机种子
    random.seed(seed)

    G = nx.Graph()
    positions = {}
    mother_node_id = num_child_nodes  # 母节点编号

    # 随机生成节点位置
    def generate_random_position():
        """在圆形区域内生成随机位置"""
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, forest_radius)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        return x, y

    # 初始化子节点位置
    child_positions = []

    # 确保至少一个子节点距离母节点小于 bluetooth_range
    while True:
        candidate = generate_random_position()
        dist_to_mother = math.sqrt(candidate[0]**2 + candidate[1]**2)
        if dist_to_mother <= bluetooth_range:
            child_positions.append(candidate)
            break

    # 生成剩余的子节点并确保每个节点附近有其他节点
    while len(child_positions) < num_child_nodes:
        candidate = generate_random_position()
        # 计算附近节点的数量
        nearby_nodes = sum(
            math.sqrt((candidate[0] - p[0])**2 + (candidate[1] - p[1])**2) <= bluetooth_range
            for p in child_positions
        )
        if nearby_nodes >= min_neighbors:
            child_positions.append(candidate)

    # 添加子节点到图中
    for i, pos in enumerate(child_positions):
        G.add_node(i, energy=initial_energy, role="child")  # 子节点初始能量为传入的参数
        positions[i] = pos

    # 添加母节点到图中
    G.add_node(mother_node_id, energy=float('inf'), role="mother")  # 母节点能量无限
    positions[mother_node_id] = (0, 0)  # 母节点固定在森林中央 (0, 0)

    k = 0.01  # 蓝牙通信功率系数（单位：W/m²）

    # 添加子节点与母节点的边（蓝牙通信范围和权重）
    for i in range(num_child_nodes):
        dist_to_mother = math.sqrt(child_positions[i][0]**2 + child_positions[i][1]**2)
        if dist_to_mother <= bluetooth_range:  # 使用蓝牙通信范围限制
            weight = k * dist_to_mother ** 2  # 添加比例系数 k
            G.add_edge(i, mother_node_id, weight=weight)

    # 添加子节点之间的边（蓝牙通信范围和权重）
    for i in range(num_child_nodes):
        for j in range(i + 1, num_child_nodes):
            dist = math.sqrt(
                (child_positions[i][0] - child_positions[j][0])**2 +
                (child_positions[i][1] - child_positions[j][1])**2
            )
            if dist <= bluetooth_range:  # 使用蓝牙通信范围限制
                weight = k * dist ** 2  # 添加比例系数 k
                G.add_edge(i, j, weight=weight)

    return G, positions, mother_node_id


# 可视化生成的图
def visualize_graph(G, positions, mother_node_id, save_path=None):
    plt.figure(figsize=(10, 10))
    nx.draw(
        G,
        pos=positions,
        with_labels=True,
        node_color=[
            "red" if node == mother_node_id else "green" for node in G.nodes
        ],
        node_size=1000,
        font_size=16,
        edge_color="gray",
        width=2,
    )
    # plt.title("Forest Graph with Central Mother Node", fontsize=16)

    # 如果设置了保存路径，则保存图像
    if save_path:
        plt.savefig(save_path, format="png", dpi=300, bbox_inches="tight")  # DPI设置为300，高清保存
        print(f"Graph saved as {save_path}")
    else:
        plt.show()


def highlight_shortest_paths_with_arrows(G, positions, mother_node_id, target_nodes, save_path=None):
    """
    在图上高亮显示目标节点到母节点的最短路径，并用箭头表示边。

    Args:
        G (networkx.DiGraph): 图对象（有向图）。
        positions (dict): 节点的位置字典。
        mother_node_id (int): 母节点的编号。
        target_nodes (list): 需要高亮最短路径的目标节点列表。
        save_path (str): 保存图像的路径（如果为 None，则直接显示图像）。
    """
    # 计算目标节点到母节点的最短路径
    shortest_paths = {}
    for target_node in target_nodes:
        try:
            path = nx.shortest_path(G, source=target_node, target=mother_node_id, weight="weight")
            shortest_paths[target_node] = path
        except nx.NetworkXNoPath:
            print(f"No path found between node {target_node} and the mother node.")

    # 提取路径中的边
    highlighted_edges = []
    for path in shortest_paths.values():
        highlighted_edges.extend([(path[i], path[i + 1]) for i in range(len(path) - 1)])

    # 可视化
    plt.figure(figsize=(10, 10))
    
    # 普通边
    nx.draw_networkx_edges(
        G,
        pos=positions,
        edgelist=[e for e in G.edges if e not in highlighted_edges],
        edge_color="gray",
        width=2,
    )
    
    # 高亮路径边
    nx.draw_networkx_edges(
        G,
        pos=positions,
        edgelist=highlighted_edges,
        edge_color="blue",
        width=4,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=30,
    )
    
    # 节点
    nx.draw_networkx_nodes(
        G,
        pos=positions,
        node_color=["red" if node == mother_node_id else "green" for node in G.nodes],
        node_size=1000,
    )
    
    # 标签
    nx.draw_networkx_labels(G, pos=positions, font_size=16)

    # 如果设置了保存路径，则保存图像
    if save_path:
        plt.savefig(save_path, format="png", dpi=300, bbox_inches="tight")
        print(f"Graph with highlighted paths saved as {save_path}")
    else:
        plt.show()

# 使用该函数生成并可视化
if __name__ == "__main__":
    G, positions, mother_node_id = build_forest_graph(num_child_nodes=10, seed=3)
    
    # 可视化原始图
    # visualize_graph(G, positions, mother_node_id, save_path="forest_graph_10.png")
    
    # 高亮显示节点 5 和 9 到母节点的最短路径
    highlight_shortest_paths_with_arrows(G, positions, mother_node_id, target_nodes=[0,1,2,3,4,5,6,7,8, 9], save_path="highlighted_paths_with_arrows.png")