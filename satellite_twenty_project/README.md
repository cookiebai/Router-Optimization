# Satellite Twenty-Node Mininet Topology

This project packages the customised twenty-node Mininet topology and the associated routing optimisation logic. It reproduces the hierarchical core/aggregation/access design described in `satellite_twenty.py` and applies deterministic shortest-path forwarding via `satellite_twenty_algorithm.py`.

## Features
- Two core, four aggregation, eight access switches with sixteen hosts total.
- Deterministic datapath IDs for every switch to simplify controller integration.
- Optional static routing optimisation that calculates latency-weighted shortest paths with NetworkX and installs OpenFlow rules directly on each switch.
- STP-based fallback mode when optimisation is disabled.

## Project Layout
```
satellite_twenty_project/
├── README.md
├── requirements.txt
└── src/
    └── satellite_topology/
        ├── __init__.py
        ├── satellite_twenty.py
        └── satellite_twenty_algorithm.py
```
- `satellite_twenty.py`: entry point that builds the Mininet topology, handles CLI flags, and optionally invokes the optimiser.
- `satellite_twenty_algorithm.py`: isolates the NetworkX workflow and flow-installation logic.
- `requirements.txt`: Python dependencies required in addition to Mininet itself.

## Prerequisites
1. **Python**: 3.8+ (tested with 3.10).
2. **Mininet 2.3.0** (install via apt or from source):
   ```bash
   sudo apt update
   sudo apt install mininet
   ```
3. **Open vSwitch** is installed automatically with Mininet on Ubuntu; ensure kernel modules are loaded.
4. **Python packages** listed in `requirements.txt` (NetworkX).

## Setup
```bash
cd satellite_twenty_project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
> Note: Mininet itself should remain a system-level install; do not attempt to pip-install it into the virtual environment.

## Running the Topology
All Mininet runs must be executed with root privileges:
```bash
sudo -E env PATH="$PATH" python src/satellite_topology/satellite_twenty.py [options]
```
Supported options:
- `-o/--optimize`: disable STP, clear default flows, run the optimisation routine, and push static rules. Recommended for deterministic routing.
- `-c/--controller <IP>`: connect switches to a remote OpenFlow controller (disables standalone bridge mode). When using a controller, omit `--optimize` unless the controller is aware of the static rules.

Example (standalone with optimisation):
```bash
sudo python src/satellite_topology/satellite_twenty.py -o
```
Example (standalone L2 bridging with STP):
```bash
sudo python src/satellite_topology/satellite_twenty.py
```

## Verifying Connectivity
The script automatically runs `net.pingAll()` once the topology is up. You can also perform manual checks from the Mininet CLI:
```bash
mininet> pingall
mininet> h1 ping -c3 h9
mininet> exit
```
Expect `0%` packet loss when optimisation is enabled.

## Customisation Tips
- Adjust link parameters (bandwidth, delay) inside `satellite_twenty.py` when modelling different satellite backhaul characteristics.
- Modify or extend `satellite_twenty_algorithm.optimize_routing()` to apply alternative path metrics or intent-based provisioning.
- The default drop rule inserted before optimisation prevents unintended flooding loops; retain it unless you add your own controller logic.

## Troubleshooting
- **`sch_htb ... quantum ... big` warnings**: benign TC warning triggered by high bandwidth with low delay. Reduce `bw` or raise `--link`'s `r2q` if precise queue behaviour is required.
- **`RTNETLINK answers: File exists`**: run `sudo mn -c` to clean stale namespaces and interfaces before re-running the topology.
- **Permission errors**: always use `sudo` (or run inside a privileged container/VM) because Mininet manipulates network namespaces.

## License
Provided as-is for internal experimentation. Review Mininet and Open vSwitch licenses before redistribution.
