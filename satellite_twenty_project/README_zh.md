# 卫星二十节点 Mininet 拓扑

该项目封装了定制的二十节点 Mininet 拓扑及其路由优化算法，实现核心/汇聚/接入三层结构，并通过 `satellite_twenty_algorithm.py` 提供基于 NetworkX 的确定性转发。

## 功能亮点
- 双核心、四汇聚、八接入交换机组成的层次化拓扑，共 16 台主机。
- 每台交换机构造固定 DPID，便于外部控制器识别。
- 可选的静态路由优化：使用 NetworkX 计算按延迟加权的最短路径，并通过 OpenFlow 规则下发至各交换机。
- 未启用优化时自动开启 STP，保证二层环路安全。

## 目录结构
```
satellite_twenty_project/
├── README.md
├── README_zh.md
├── requirements.txt
└── src/
    └── satellite_topology/
        ├── __init__.py
        ├── satellite_twenty.py
        └── satellite_twenty_algorithm.py
```
- `satellite_twenty.py`：程序入口，构建拓扑、解析参数并调用优化器。
- `satellite_twenty_algorithm.py`：独立的 NetworkX 计算与流表下发逻辑。
- `requirements.txt`：除 Mininet 外所需的 Python 依赖。

## 环境依赖
1. **Python 3.8+**（实测 3.10 可用）。
2. **Mininet 2.3.0**：
   ```bash
   sudo apt update
   sudo apt install mininet
   ```
3. **Open vSwitch**：Ubuntu 上随 Mininet 安装，确保内核模块已加载。
4. **Python 包**：执行 `pip install -r requirements.txt` 安装 NetworkX。

## 初始化步骤
```bash
cd satellite_twenty_project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
> 注意：Mininet 建议通过系统包安装，不要尝试在虚拟环境中 `pip install`。

## 运行方式
运行 Mininet 需要 root 权限：
```bash
sudo -E env PATH="$PATH" python src/satellite_topology/satellite_twenty.py [参数]
```
可选参数：
- `-o/--optimize`：关闭 STP、清空默认流表并执行优化算法，安装静态路径（推荐）。
- `-c/--controller <IP>`：连接到远程 OpenFlow 控制器。使用控制器时通常不要再启用 `--optimize`，除非控制器理解这些静态规则。

示例（独立模式 + 优化）：
```bash
sudo python src/satellite_topology/satellite_twenty.py -o
```
示例（纯二层桥接，依赖 STP）：
```bash
sudo python src/satellite_topology/satellite_twenty.py
```

## 连通性验证
脚本会自动执行一次 `net.pingAll()`。也可在 CLI 中手动测试：
```bash
mininet> pingall
mininet> h1 ping -c3 h9
mininet> exit
```
优化开启时应看到 `0% dropped`。

## 定制建议
- 在 `satellite_twenty.py` 中调整链路带宽/时延模拟不同卫星链路。
- 修改 `satellite_twenty_algorithm.optimize_routing()` 以支持自定义指标或策略。
- 默认在安装流表前先添加低优先级 drop 规则，避免未知流量泛洪；如使用外部控制器，请确保策略一致。

## 常见问题
- **`sch_htb ... quantum ... big`**：高带宽+低延迟导致的 TC 警告，不影响功能。需要精确排队时可降低 `bw` 或调整 `r2q`。
- **`RTNETLINK answers: File exists`**：说明上一次运行未清理干净，执行 `sudo mn -c` 后再启动。
- **权限不足**：Mininet 需 root 权限，务必使用 `sudo` 或在具备特权的容器/虚拟机中运行。

## 许可证
此项目作为内部实验用途提供。发布前请查阅 Mininet 与 Open vSwitch 的许可证要求。
