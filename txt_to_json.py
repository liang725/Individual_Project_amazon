import json
from collections import Counter
from tqdm import tqdm


def _parse_nodes_generator(file_path):
    # 逐行解析，一次 yield 一个节点
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        current_node = {}
        for line in f:
            line = line.strip()
            if line.startswith('Id:'):
                if current_node and 'id' in current_node and 'group' in current_node:
                    yield current_node
                current_node = {'id': line.split(':')[1].strip()}
            elif line.startswith('title:') and 'id' in current_node:
                current_node['title'] = line.split(':', 1)[1].strip()
            elif line.startswith('group:') and 'id' in current_node:
                current_node['group'] = line.split(':')[1].strip()
        if current_node and 'id' in current_node and 'group' in current_node:
            yield current_node


def parse_amazon_meta_optimized(file_path, max_nodes=100):
    # 单遍扫描，取前 max_nodes 且满足分布要求
    print(f"Finding first {max_nodes} nodes with group distribution requirements...")
    selected_nodes = []
    group_counts = Counter()
    total_count = 0
    node_generator = _parse_nodes_generator(file_path)

    for node in tqdm(node_generator, desc="Scanning nodes"):
        selected_nodes.append(node)
        group_counts[node['group']] += 1
        total_count += 1
        sorted_groups = group_counts.most_common(3)

        if (sorted_groups[0][1] / total_count) > 0.4:
            continue
        if len(sorted_groups) > 1 and (sorted_groups[1][1] / total_count) > 0.3:
            continue
        if len(sorted_groups) > 2 and (sorted_groups[2][1] / total_count) > 0.2:
            continue
        if total_count >= max_nodes:
            print(f"\nFound suitable prefix of {total_count} nodes. Taking first {max_nodes}.")
            break

    final_nodes = selected_nodes[:max_nodes]
    if len(final_nodes) < max_nodes:
        print(f"\nWarning: Only {len(final_nodes)} nodes meet criteria. Using them.")
    final_group_counts = Counter(node['group'] for node in final_nodes)
    print(f"\nGroup distribution for {len(final_nodes)} nodes:")
    for group, count in final_group_counts.most_common():
        percentage = (count / len(final_nodes)) * 100
        print(f"  {group}: {count} ({percentage:.1f}%)")
    return final_nodes


def parse_amazon_edges_optimized(file_path, valid_node_ids):
    # 逐行读边，只保留两端都在 valid 里的
    print("\nReading amazon0302.txt...")
    edges = []
    valid_ids = set(valid_node_ids)
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Processing edges"):
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) == 2:
                source, target = parts[0], parts[1]
                if source in valid_ids and target in valid_ids:
                    edges.append({'source': source, 'target': target})
    print(f"Total valid edges: {len(edges)}")
    return edges


def create_amazon_json_optimized(meta_file, edges_file, output_file, max_nodes=50):
    # 主入口：生成前端可直接读的 amazon.json
    nodes_data = parse_amazon_meta_optimized(meta_file, max_nodes)
    valid_node_ids = {node['id'] for node in nodes_data}

    id_to_title = {}
    nodes = []
    for node in nodes_data:
        node_id = node['id']
        title = node.get('title', f"Product_{node_id}")
        group = node['group']
        full_id_str = f"{node_id}: {title}"
        id_to_title[node_id] = full_id_str
        nodes.append({'id': full_id_str, 'group': group})

    edges_data = parse_amazon_edges_optimized(edges_file, valid_node_ids)
    links = []
    for edge in edges_data:
        if edge['source'] in id_to_title and edge['target'] in id_to_title:
            links.append({'source': id_to_title[edge['source']],
                          'target': id_to_title[edge['target']],
                          'value': 1})

    result = {'nodes': nodes, 'links': links}
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Successfully created {output_file}")
    print(f"Nodes: {len(nodes)}, Links: {len(links)}")


if __name__ == "__main__":
    create_amazon_json_optimized(
        meta_file='amazon-meta.txt',
        edges_file='amazon0302.txt',
        output_file='amazon-copurchase-network-visualizer/data_files/amazon.json',
        max_nodes=100
    )
