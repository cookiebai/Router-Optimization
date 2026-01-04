#!/usr/bin/env python

"""
Mininet 2.3.0 拓扑示例
包含20个节点的网络拓扑
作者: Mininet用户
版本: 1.0
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSBridge, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import argparse
import time

from satellite_twenty_algorithm import optimize_routing

class TwentyNodeTopo(Topo):
    """
    包含20个节点的自定义拓扑
    网络结构: 
      - 核心层: 2个核心交换机
      - 汇聚层: 4个汇聚交换机
      - 接入层: 8个接入交换机
      - 主机: 16个主机
    """
    
    def __init__(self, **opts):
        """初始化拓扑"""
        Topo.__init__(self, **opts)
        
        # 添加核心层交换机 (2个)
        core1 = self.addSwitch('c1', dpid='0000000000000001')
        core2 = self.addSwitch('c2', dpid='0000000000000002')
        
        # 添加汇聚层交换机 (4个)
        agg_switches = []
        for i in range(1, 5):
            agg_switch = self.addSwitch('a%d' % i, dpid='00000000000000%02d' % (i+2))
            agg_switches.append(agg_switch)
            
            # 连接核心层和汇聚层
            # 每个汇聚交换机连接到两个核心交换机
            self.addLink(agg_switch, core1, bw=10, delay='1ms')
            self.addLink(agg_switch, core2, bw=10, delay='1ms')
        
        # 添加接入层交换机 (8个)
        acc_switches = []
        host_index = 1
        
        for i in range(1, 9):
            # 使用16位十六进制DPID，避免长度不足导致OVS警告
            acc_switch = self.addSwitch('s%d' % i, dpid='00000000000000%02d' % (i+6))
            acc_switches.append(acc_switch)
            
            # 连接汇聚层和接入层
            # 每个接入交换机连接到一个汇聚交换机
            agg_index = (i-1) // 2  # 每两个接入交换机连接到一个汇聚交换机
            self.addLink(acc_switch, agg_switches[agg_index], bw=5, delay='2ms')
            
            # 为每个接入交换机添加2个主机
            for j in range(1, 3):
                host_name = 'h%d' % host_index
                host = self.addHost(host_name, 
                                   ip='10.0.0.%d/24' % host_index,
                                   mac='00:00:00:00:00:%02d' % host_index)
                self.addLink(host, acc_switch, bw=2, delay='1ms')
                host_index += 1
        
        # 连接两个核心交换机，形成骨干
        self.addLink(core1, core2, bw=20, delay='0.5ms')

def run():
    """启动网络并运行CLI"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Run 20-node topology')
    parser.add_argument('--controller', '-c', help='Controller IP address (e.g., 127.0.0.1)', default=None)
    parser.add_argument('--optimize', '-o', action='store_true', help='Enable static routing optimization (Dijkstra)')
    args = parser.parse_args()

    # 创建拓扑
    topo = TwentyNodeTopo()
    
    # 创建网络
    if args.controller:
        info(f"*** Connecting to remote controller at {args.controller}\n")
        net = Mininet(topo=topo,
                      controller=lambda name: RemoteController(name, ip=args.controller, port=6653),
                      switch=OVSSwitch,
                      link=TCLink,
                      autoSetMacs=True,
                      autoStaticArp=True)
    elif args.optimize:
        info("*** Using standalone OVSSwitch mode with Static Routing Optimization\n")
        net = Mininet(topo=topo,
                      controller=None,
                      switch=OVSSwitch,
                      link=TCLink,
                      autoSetMacs=True,
                      autoStaticArp=True)
    else:
        info("*** Using standalone OVSBridge mode (no controller)\n")
        net = Mininet(topo=topo,
                      controller=None,        # 本地二层桥接模式，无需控制器
                      switch=OVSBridge,
                      link=TCLink,
                      autoSetMacs=True,
                      autoStaticArp=True)
    
    # 启动网络
    net.start()
    
    # 如果开启了优化模式，计算并下发流表
    if args.optimize:
        # 清理默认流表，防止未知流量在环路中泛洪；随后下发静态最优路径
        for s in net.switches:
            s.cmd('ovs-ofctl del-flows %s' % s.name)
            s.cmd('ovs-ofctl add-flow %s priority=0,actions=drop' % s.name)
        optimize_routing(net)
    # 如果是独立模式且未开启优化，启用 STP
    elif not args.controller:
        info("*** Enabling STP and waiting 45s for convergence...\n")
        # 启用所有交换机的 STP，避免环路导致广播风暴
        for s in net.switches:
            s.cmd('ovs-vsctl set bridge %s stp_enable=true' % s.name)
        time.sleep(45)
    
    # 输出网络信息
    info("*** 网络已启动，包含20个节点 ***\n")
    info("*** 拓扑结构：\n")
    info("    核心层: c1, c2\n")
    info("    汇聚层: a1, a2, a3, a4\n")
    info("    接入层: s1-s8\n")
    info("    主机: h1-h16\n")
    info("*** 使用CLI进行网络测试\n")
    
    # 运行一次连通性测试
    net.pingAll()
    # 启动CLI
    CLI(net)
    
    # 关闭网络
    net.stop()


if __name__ == '__main__':
    # 设置日志级别
    setLogLevel('info')
    
    # 运行网络
    run()