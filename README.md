# 🚚 Logistics-Lattice: Agentic Supply Chain Digital Twin

An autonomous supply chain resilience system that uses a **Graph Database** to detect, analyze, and autonomously resolve logistics disruptions in real-time.

## 🎯 Overview

Logistics-Lattice is an Agentic Supply Chain Digital Twin that leverages Neo4j graph database technology to create a living model of a logistics network. When disruptions occur (truck failures, route blockages), autonomous agents automatically reroute packages, minimize delays, and calculate the impact on SLA commitments.

## ✨ Core Features

### 1. 📊 Graph Data Model (Neo4j)
- **Nodes**: Truck, Package, Warehouse, Customer, RoutePoint
- **Relationships**: 
  - `(:Truck)-[:CARRYING]->(:Package)` - Trucks carrying packages
  - `(:Truck)-[:LOCATED_AT]->(:RoutePoint)` - Truck locations
  - `(:Package)-[:DESTINED_FOR]->(:Customer)` - Package destinations
- **Geospatial properties** for distance calculations

### 2. 🎲 Disruption Listener (Chaos Events)
- Simulates real-world logistics disruptions
- Event types:
  - 🔥 Truck failures (engine failure, tire blowout, etc.)
  - 🚧 Route blockages (floods, accidents, construction)
- Configurable chaos injection probability
- Event severity levels (low, medium, high, critical)

### 3. 🤖 Autonomous Re-Routing Agent (LangGraph)
- **Trigger**: Automatically activates when truck failures are detected
- **Query Logic**: Finds nearest available trucks using geospatial Euclidean distance
- **Selection Criteria**: 
  - Available capacity > package weight
  - Same direction of travel
  - Minimum distance to failed truck location
- **Action**: Updates graph to transfer packages and recalculates ETAs

### 4. 📈 Impact Observability Dashboard (Streamlit)
- Real-time visualization of the logistics network
- **Blast Radius Analysis**: Shows the impact of each disruption
  - Number of late deliveries
  - Affected customers
  - SLA penalty costs
- Interactive map of truck locations
- Fleet capacity utilization charts
- Live event log

## 🛠️ Tech Stack

- **Python 3.8+**: Core programming language
- **Neo4j**: Graph database for network modeling
- **LangGraph**: Agent workflow orchestration
- **Streamlit**: Interactive dashboard
- **Plotly**: Data visualization
- **Google Maps API**: (Optional) Real routing and distance calculations

## 📦 Installation

### Prerequisites

1. **Neo4j Database**: Install and start Neo4j
   ```bash
   # Download from: https://neo4j.com/download/
   # Or use Docker:
   docker run -d \
     --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest
   ```

2. **Python 3.8+**: Ensure Python is installed
   ```bash
   python --version
   ```

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yadavanujkumar/Supply-Chain-Resilience-Graph.git
   cd Supply-Chain-Resilience-Graph
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j credentials
   ```

4. **Initialize the database**
   ```bash
   python main.py setup
   ```

5. **Load sample data**
   ```bash
   python main.py load-data --trucks 10 --packages 30
   ```

## 🚀 Usage

### Command-Line Interface

```bash
# Test Neo4j connection
python main.py test

# Load sample logistics data
python main.py load-data --trucks 15 --packages 50

# Run chaos simulation
python main.py simulate --duration 120

# Launch interactive dashboard
python main.py dashboard
```

### Dashboard

The Streamlit dashboard provides a real-time view of your logistics network:

```bash
python main.py dashboard
# Or directly:
streamlit run dashboard.py
```

**Dashboard Features:**
- 🗺️ **Interactive Map**: See all truck locations in real-time
- 📊 **Metrics**: Fleet status, active events, packages in transit
- 💥 **Blast Radius**: Impact analysis for each disruption
- 🎮 **Controls**: Manually inject chaos events
- 📜 **Event Log**: Historical view of all disruptions

### Programmatic Usage

```python
from graph_model import LogisticsGraph
from disruption_simulator import DisruptionSimulator
from rerouting_agent import AutonomousReroutingAgent

# Connect to graph database
graph = LogisticsGraph()
graph.connect()

# Initialize components
simulator = DisruptionSimulator(graph)
agent = AutonomousReroutingAgent(graph)

# Inject a disruption
event = simulator.inject_truck_failure("TRUCK-001")

# Agent automatically handles rerouting
result = agent.handle_truck_failure("TRUCK-001")
print(f"Rerouted {len(result['rerouting_plan'])} packages")

graph.close()
```

## 📁 Project Structure

```
Supply-Chain-Resilience-Graph/
├── config.py                  # Configuration and environment variables
├── graph_model.py             # Neo4j graph data model and operations
├── disruption_simulator.py    # Chaos event injection system
├── rerouting_agent.py         # Autonomous rerouting agent (LangGraph)
├── data_loader.py             # Sample data initialization
├── dashboard.py               # Streamlit dashboard
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment configuration template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔧 Configuration

Edit `.env` file to configure:

```env
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Optional: Google Maps API
GOOGLE_MAPS_API_KEY=your_api_key

# Optional: OpenAI API (for advanced LangGraph features)
OPENAI_API_KEY=your_openai_key
```

## 🎯 Key Algorithms

### Geospatial Distance Calculation
Uses **Euclidean distance** for fast proximity queries:
```cypher
MATCH (t:Truck)
WHERE t.status = 'active' AND t.available_capacity >= $min_capacity
WITH t, sqrt(power(t.current_lat - $lat, 2) + power(t.current_lon - $lon, 2)) AS distance
RETURN t, distance
ORDER BY distance
```

### Blast Radius Calculation
Analyzes the impact of truck failures:
```cypher
MATCH (t:Truck {truck_id: $truck_id})-[:CARRYING]->(p:Package)-[:DESTINED_FOR]->(c:Customer)
RETURN count(p) as affected_packages,
       count(DISTINCT c) as affected_customers
```

## 🧪 Example Scenarios

### Scenario 1: Single Truck Failure
```bash
python main.py load-data --trucks 10 --packages 30
python main.py dashboard
# In dashboard: Click "Inject Failure" on a truck
# Watch the autonomous agent reroute packages
```

### Scenario 2: Cascading Failures
```python
from disruption_simulator import ChaosEventGenerator
events = ChaosEventGenerator.generate_cascading_failures(
    graph, "TRUCK-001", cascade_probability=0.5
)
# Simulates a failure that triggers nearby truck failures
```

### Scenario 3: Weather Event
```python
events = ChaosEventGenerator.generate_weather_event(
    graph, affected_region=(40.0, -74.0, 2.0)
)
# Simulates weather affecting trucks in a geographic region
```

## 📊 Performance Metrics

The system tracks:
- **Rerouting Success Rate**: Percentage of successful package transfers
- **Average Response Time**: Time to reroute after disruption
- **SLA Compliance**: Percentage of on-time deliveries
- **Cost Impact**: Total SLA penalties from delays

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Neo4j](https://neo4j.com/) graph database
- Powered by [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- Visualized with [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/)

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ for resilient supply chains**