# Quick Start Guide - Logistics-Lattice

This guide will help you get Logistics-Lattice up and running quickly.

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] Neo4j database running (see below)
- [ ] Basic understanding of graph databases (optional)

## Step-by-Step Setup

### 1. Install Neo4j

**Option A: Docker (Recommended)**
```bash
docker run -d \
  --name neo4j-logistics \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

**Option B: Download Desktop**
- Download from: https://neo4j.com/download/
- Install and start Neo4j Desktop
- Create a new database with password: `password`

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yadavanujkumar/Supply-Chain-Resilience-Graph.git
cd Supply-Chain-Resilience-Graph

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Neo4j credentials (default: neo4j/password)
```

### 3. Initialize the System

```bash
# Test Neo4j connection
python main.py test

# Initialize database schema
python main.py setup

# Load sample data (10 trucks, 30 packages)
python main.py load-data
```

### 4. Launch the Dashboard

```bash
python main.py dashboard
```

The dashboard will open in your browser at http://localhost:8501

## Dashboard Features

### Main View
- **Truck Map**: Interactive map showing all truck locations
- **Metrics**: Real-time statistics on fleet status
- **Capacity Chart**: Visual representation of truck utilization

### Disruption Controls (Sidebar)
1. **Select Event Type**: Choose "Truck Failure" or "Route Blockage"
2. **Select Target**: Pick a specific truck or random
3. **Inject Failure**: Click to simulate disruption
4. **Watch Auto-Rerouting**: The autonomous agent will automatically reroute affected packages

### Blast Radius Analysis
When a truck fails, you'll see:
- Number of affected deliveries
- Affected customers
- Estimated delay in hours
- SLA penalties in dollars
- Impact summary

## Example Workflow

### Simulate a Truck Failure

1. **Start the dashboard**
   ```bash
   python main.py dashboard
   ```

2. **Observe the initial state**
   - Note the number of active trucks
   - Check package distribution

3. **Inject a failure**
   - Sidebar → Select "Truck Failure"
   - Choose a truck (or Random)
   - Click "💥 Inject Failure"

4. **Watch the autonomous response**
   - Event appears in the log
   - Blast radius is calculated
   - Agent automatically reroutes packages
   - Map updates with new truck assignments

5. **Analyze the impact**
   - Check the blast radius analysis
   - Review SLA penalties
   - See which packages were affected

### Run a Continuous Simulation

```bash
# Run simulation for 2 minutes (120 seconds)
python main.py simulate --duration 120
```

This will:
- Randomly inject disruptions every 10 seconds
- Print events to console
- Show rerouting operations
- Display final statistics

## Programmatic Usage

```python
from graph_model import LogisticsGraph
from disruption_simulator import DisruptionSimulator
from rerouting_agent import AutonomousReroutingAgent

# Connect to database
graph = LogisticsGraph()
graph.connect()

# Create components
simulator = DisruptionSimulator(graph)
agent = AutonomousReroutingAgent(graph)

# Simulate disruption
event = simulator.inject_truck_failure("TRUCK-005")

# Agent handles rerouting
result = agent.handle_truck_failure("TRUCK-005")
print(f"Rerouted {len(result['rerouting_plan'])} packages")

# Analyze impact
from rerouting_agent import calculate_blast_radius
impact = calculate_blast_radius(graph, "TRUCK-005")
print(impact["impact_summary"])

graph.close()
```

## Customization

### Adjust Simulation Parameters

Edit `config.py`:
```python
SIMULATION_INTERVAL = 10      # Seconds between disruption checks
SLA_PENALTY_PER_HOUR = 10     # Dollars per hour of delay
TRUCK_SPEED_KMH = 60          # Average truck speed
```

### Load Custom Data

```python
from graph_model import LogisticsGraph

graph = LogisticsGraph()
graph.connect()

# Create custom entities
graph.create_truck("TRUCK-CUSTOM", capacity=3000, 
                  current_lat=40.0, current_lon=-74.0)
graph.create_customer("CUST-CUSTOM", name="My Customer",
                     lat=41.0, lon=-73.0, sla_hours=24)

graph.close()
```

### Change Fleet Size

```bash
# Load more trucks and packages
python main.py load-data --trucks 20 --packages 100
```

## Troubleshooting

### "Failed to connect to Neo4j"
- Ensure Neo4j is running: `docker ps` or check Neo4j Desktop
- Verify credentials in `.env` file
- Check that port 7687 is not blocked

### "No module named 'neo4j'"
- Install dependencies: `pip install -r requirements.txt`
- Ensure virtual environment is activated

### Dashboard won't start
- Check if port 8501 is available
- Try: `streamlit run dashboard.py --server.port 8502`

### No trucks appear
- Make sure you ran: `python main.py load-data`
- Check database: Run `python main.py test`

## Next Steps

1. **Explore the Code**: Read through the well-documented source files
2. **Customize the Schema**: Add new node types or relationships
3. **Integrate Real APIs**: Connect Google Maps API for real routing
4. **Add More Agents**: Create agents for other scenarios
5. **Scale Up**: Load hundreds of trucks and packages

## Support

- GitHub Issues: https://github.com/yadavanujkumar/Supply-Chain-Resilience-Graph/issues
- Documentation: See README.md for detailed documentation

---

**Happy Disruption Testing! 🚚💥**
