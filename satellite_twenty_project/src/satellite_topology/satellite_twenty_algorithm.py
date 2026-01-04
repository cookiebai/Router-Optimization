"""Routing optimization logic for satellite_twenty topology."""

import networkx as nx
from mininet.log import info
from mininet.node import OVSBridge


def optimize_routing(net):
    """Use NetworkX shortest paths (latency weight) to install static flows."""
    info("*** Calculating optimized paths using NetworkX...\n")

    # 1. Build NetworkX graph with delay weights
    graph = nx.Graph()
    for link in net.links:
        node1, node2 = link.intf1.node, link.intf2.node
        delay_str = link.intf1.params.get('delay', '1ms')
        delay = float(delay_str.replace('ms', ''))
        graph.add_edge(
            node1.name,
            node2.name,
            weight=delay,
            port1=link.intf1.name,
            port2=link.intf2.name,
        )

    # 2. Compute per-host shortest paths and push flows
    hosts = net.hosts
    for src in hosts:
        for dst in hosts:
            if src == dst:
                continue

            try:
                path = nx.shortest_path(graph, src.name, dst.name, weight='weight')
            except nx.NetworkXNoPath:
                continue

            dst_mac = dst.MAC()

            for i in range(1, len(path) - 1):
                current_node_name = path[i]
                next_node_name = path[i + 1]

                current_node = net.get(current_node_name)
                if not isinstance(current_node, OVSBridge) and not hasattr(current_node, 'dpctl'):
                    pass

                edge_data = graph.get_edge_data(current_node_name, next_node_name)
                if edge_data['port1'].startswith(current_node_name + '-'):
                    out_port_name = edge_data['port1']
                else:
                    out_port_name = edge_data['port2']

                out_port = current_node.ports[current_node.nameToIntf[out_port_name]]

                cmd = 'ovs-ofctl add-flow %s priority=100,dl_dst=%s,actions=output:%s' % (
                    current_node.name,
                    dst_mac,
                    out_port,
                )
                current_node.cmd(cmd)

    info("*** Optimized static flows installed.\n")
