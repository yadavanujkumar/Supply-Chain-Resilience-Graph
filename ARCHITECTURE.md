# Logistics-Lattice Architecture

## System Overview

Logistics-Lattice is an autonomous supply chain resilience system built on a graph database foundation. The system continuously monitors a logistics network, detects disruptions, and automatically reroutes packages to minimize delays and costs.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interfaces                              │
├─────────────────────────────────────────────────────────────────┤
│  Streamlit Dashboard  │  CLI (main.py)  │  Python API          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Disruption      │  │  Rerouting       │  │  Impact      │  │
│  │  Simulator       │  │  Agent           │  │  Analyzer    │  │
│  │  (Chaos Events)  │  │  (LangGraph)     │  │              │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Model Layer                             │
├─────────────────────────────────────────────────────────────────┤
│                   Graph Model (graph_model.py)                   │
│  - Node operations (Truck, Package, Customer, etc.)             │
│  - Relationship management (CARRYING, LOCATED_AT, etc.)         │
│  - Geospatial queries                                           │
│  - Impact analysis                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Database Layer                               │
├─────────────────────────────────────────────────────────────────┤
│                      Neo4j Graph Database                        │
│  - Nodes: Truck, Package, Warehouse, Customer, RoutePoint      │
│  - Relationships: CARRYING, LOCATED_AT, DESTINED_FOR           │
│  - Indexes & Constraints                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Database Layer (Neo4j)

**Purpose**: Store and query the logistics network as a graph

**Node Types**:
- **Truck**: Moving assets that carry packages
  - Properties: truck_id, capacity, available_capacity, current_lat, current_lon, status, direction
- **Package**: Items being transported
  - Properties: package_id, weight, destination_lat, destination_lon, status, priority, expected_eta
- **Warehouse**: Distribution centers
  - Properties: warehouse_id, name, lat, lon, capacity
- **Customer**: Delivery destinations
  - Properties: customer_id, name, lat, lon, sla_hours
- **RoutePoint**: Waypoints in the logistics network
  - Properties: point_id, name, lat, lon, type, status

**Relationships**:
- `(:Truck)-[:CARRYING]->(:Package)` - Package assignment
- `(:Truck)-[:LOCATED_AT]->(:RoutePoint)` - Current location
- `(:Package)-[:DESTINED_FOR]->(:Customer)` - Delivery destination

**Advantages**:
- Natural representation of network topology
- Efficient traversal for finding alternative routes
- Geospatial queries for proximity-based decisions
- ACID transactions for data integrity

### 2. Data Model Layer (graph_model.py)

**Purpose**: Abstract Neo4j operations into a clean Python API

**Key Classes**:
- `LogisticsGraph`: Main interface to the graph database

**Key Operations**:
- Node CRUD: create_truck(), create_package(), etc.
- Relationship management: assign_package_to_truck(), etc.
- Queries: get_all_trucks(), find_nearest_available_trucks(), etc.
- Analysis: get_impact_analysis()

**Design Patterns**:
- Repository pattern for data access
- Connection pooling via Neo4j driver
- Transaction management for atomic operations

### 3. Application Layer

#### 3.1 Disruption Simulator (disruption_simulator.py)

**Purpose**: Inject chaos events to test system resilience

**Components**:
- `DisruptionEvent`: Represents a single disruption
- `DisruptionSimulator`: Manages event injection
- `ChaosEventGenerator`: Creates realistic disruption patterns

**Event Types**:
- Truck failures (engine, tire, transmission, etc.)
- Route blockages (floods, accidents, construction)
- Weather events (regional impact)
- Cascading failures (one failure triggers others)

**Capabilities**:
- Manual single-event injection
- Continuous random simulation
- Configurable chaos probability
- Event severity levels

#### 3.2 Rerouting Agent (rerouting_agent.py)

**Purpose**: Autonomously respond to disruptions and reroute packages

**Architecture**: LangGraph state machine with 6 steps:

1. **detect_failure**: Validate truck failure
2. **assess_impact**: Calculate affected packages
3. **find_alternatives**: Query for available trucks
4. **execute_rerouting**: Transfer packages
5. **calculate_eta**: Recalculate delivery times
6. **complete**: Log results

**Key Algorithms**:
- **Geospatial Distance**: Euclidean distance for speed (suitable for regional networks)
- **Truck Selection**: Filter by capacity, direction, and proximity
- **Package Transfer**: Atomic transaction to prevent data loss

**State Management**:
```python
ReroutingState = {
    'failed_truck_id': str,
    'affected_packages': List[str],
    'available_trucks': List[Dict],
    'rerouting_plan': List[Dict],
    'status': str,
    'message': str
}
```

#### 3.3 Impact Analyzer (rerouting_agent.py)

**Purpose**: Calculate the "blast radius" of disruptions

**Metrics Calculated**:
- Number of affected deliveries
- Number of affected customers
- Estimated delay hours
- SLA penalty costs

**Formula**:
```
SLA_Penalty = affected_packages × delay_hours × penalty_per_hour
```

### 4. User Interface Layer

#### 4.1 Streamlit Dashboard (dashboard.py)

**Purpose**: Real-time visualization and control

**Features**:
- **Interactive Map**: Truck locations with status colors
- **Metrics Dashboard**: Key statistics at a glance
- **Blast Radius Analysis**: Impact of each disruption
- **Event Log**: Historical disruption timeline
- **Manual Controls**: Inject chaos events
- **Capacity Charts**: Fleet utilization visualization

**Technology**: 
- Streamlit for reactive UI
- Plotly for interactive charts
- Cached connections for performance

#### 4.2 CLI (main.py)

**Purpose**: Command-line interface for operations

**Commands**:
- `setup`: Initialize database schema
- `load-data`: Populate sample data
- `test`: Test Neo4j connection
- `simulate`: Run chaos simulation
- `dashboard`: Launch Streamlit UI

### 5. Data Initialization (data_loader.py)

**Purpose**: Populate the graph with sample logistics data

**Sample Data**:
- 4 warehouses (US geographic distribution)
- 8 customers (various SLA requirements)
- 5 route points (highways, checkpoints)
- N trucks (configurable, randomly positioned)
- M packages (configurable, randomly assigned)

## Data Flow

### Normal Operation Flow

```
1. Trucks carry packages → (:Truck)-[:CARRYING]->(:Package)
2. Packages have destinations → (:Package)-[:DESTINED_FOR]->(:Customer)
3. System monitors all truck statuses
```

### Disruption Response Flow

```
1. Disruption detected
   ↓
2. DisruptionSimulator marks truck as 'failed'
   ↓
3. ReroutingAgent triggered automatically
   ↓
4. Agent queries graph:
   - Get affected packages
   - Find nearest available trucks
   ↓
5. Agent executes transfers (atomic transactions)
   ↓
6. Agent recalculates ETAs
   ↓
7. Dashboard updates to show new state
   ↓
8. Impact analysis displayed to user
```

## Key Design Decisions

### Why Neo4j?

1. **Natural Fit**: Logistics networks are inherently graphs
2. **Query Performance**: Graph traversals are O(1) per hop
3. **Flexibility**: Easy to add new node/relationship types
4. **Geospatial Support**: Built-in spatial indexes
5. **ACID Transactions**: Data integrity for critical operations

### Why LangGraph?

1. **State Management**: Clear workflow with state transitions
2. **Debuggability**: Each step is isolated and testable
3. **Extensibility**: Easy to add new steps or branch logic
4. **Integration**: Works well with LLMs for future AI features

### Why Euclidean Distance?

1. **Performance**: Fast calculations without external API calls
2. **Sufficient Accuracy**: For regional networks (< 500km)
3. **No API Limits**: Works offline
4. **Upgradeable**: Can swap for Haversine or Google Maps API

### Why Streamlit?

1. **Rapid Development**: Dashboard built in hours, not days
2. **Reactive Updates**: Automatic UI refresh on data changes
3. **Python Native**: No separate frontend stack needed
4. **Rich Visualizations**: Plotly integration for maps and charts

## Scalability Considerations

### Current Architecture

- **Target Scale**: 100-1000 trucks, 1000-10000 packages
- **Response Time**: < 1 second for rerouting decisions
- **Geographic Scope**: Regional (single country/continent)

### Scaling Strategies

**Horizontal Scaling**:
- Neo4j cluster for distributed graph processing
- Multiple rerouting agents for parallel processing
- Load balancer for dashboard instances

**Vertical Scaling**:
- Increase Neo4j heap size
- Add more CPU cores for Cypher query processing
- SSD storage for faster graph traversals

**Optimization**:
- Spatial indexes for geospatial queries
- Connection pooling for database access
- Caching frequently accessed data
- Batch operations for bulk updates

## Security Considerations

### Current Implementation

1. **Database Access**: Environment-based credentials
2. **Input Validation**: Type checking on all inputs
3. **SQL Injection**: Parameterized Cypher queries
4. **Atomic Transactions**: Prevent data corruption
5. **No External Dependencies**: Core logic runs offline

### Future Enhancements

1. **Authentication**: User login for dashboard
2. **Authorization**: Role-based access control
3. **Encryption**: TLS for Neo4j connections
4. **Audit Logging**: Track all operations
5. **Rate Limiting**: Prevent chaos injection abuse

## Testing Strategy

### Current Tests

1. **Syntax Validation**: Python compilation checks
2. **File Structure**: Required files present
3. **Dependency Check**: All packages listed
4. **Security Scan**: CodeQL analysis

### Recommended Additional Tests

1. **Unit Tests**: Each component in isolation
2. **Integration Tests**: End-to-end workflows
3. **Performance Tests**: Query speed benchmarks
4. **Chaos Tests**: System behavior under load
5. **UI Tests**: Dashboard functionality

## Future Enhancements

### Planned Features

1. **Real Routing**: Google Maps API integration
2. **Machine Learning**: Predict disruption patterns
3. **Multi-Modal**: Add air, rail, sea transport
4. **Real-Time Data**: Live GPS tracking integration
5. **Optimization**: AI-driven route planning
6. **Notifications**: Email/SMS alerts for disruptions
7. **Historical Analysis**: Trends and patterns
8. **API Gateway**: REST/GraphQL interface

### Architectural Improvements

1. **Microservices**: Split into independent services
2. **Event Sourcing**: Audit trail of all changes
3. **CQRS**: Separate read/write models
4. **Message Queue**: Async disruption processing
5. **Multi-Tenancy**: Support multiple organizations

## Deployment

### Development

```bash
# Local Neo4j
docker-compose up neo4j

# Run application
python main.py dashboard
```

### Production

**Recommended Stack**:
- Neo4j Aura (managed graph database)
- Docker containers for application
- Kubernetes for orchestration
- Cloud storage for logs/analytics

**Environment Variables**:
- NEO4J_URI
- NEO4J_USER
- NEO4J_PASSWORD
- GOOGLE_MAPS_API_KEY (optional)
- OPENAI_API_KEY (optional)

## Monitoring

### Key Metrics

- **System Health**: Neo4j connection status
- **Performance**: Query response times
- **Business**: SLA compliance rate
- **Operations**: Rerouting success rate
- **Costs**: Total SLA penalties

### Alerting

- Truck failure rate > threshold
- Rerouting agent failures
- Database connection issues
- SLA violation predictions

## Conclusion

Logistics-Lattice demonstrates how graph databases and autonomous agents can work together to create resilient supply chain systems. The architecture is designed for clarity, extensibility, and real-world applicability while maintaining simplicity for learning and experimentation.

The system successfully implements all core requirements:
- ✅ Graph data model with Neo4j
- ✅ Disruption simulation
- ✅ Autonomous rerouting
- ✅ Impact observability

Future enhancements can build on this foundation to create production-ready supply chain resilience platforms.
