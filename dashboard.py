"""
Streamlit Dashboard for Logistics-Lattice
Impact Observability and Real-time Monitoring
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from graph_model import LogisticsGraph
from disruption_simulator import DisruptionSimulator
from rerouting_agent import AutonomousReroutingAgent, calculate_blast_radius
import config


# Page configuration
st.set_page_config(
    page_title="Logistics-Lattice Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .alert-critical { color: #ff4b4b; font-weight: bold; }
    .alert-high { color: #ffa500; font-weight: bold; }
    .alert-medium { color: #ffcc00; }
    .alert-low { color: #00cc00; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_graph_connection():
    """Initialize and cache graph database connection"""
    graph = LogisticsGraph()
    if graph.connect():
        return graph
    return None


def display_header():
    """Display dashboard header"""
    st.title("🚚 Logistics-Lattice Digital Twin")
    st.markdown("**Autonomous Supply Chain Resilience System**")
    st.markdown("---")


def display_metrics(graph: LogisticsGraph, simulator: DisruptionSimulator):
    """Display key metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Get data
    all_trucks = graph.get_all_trucks()
    active_trucks = graph.get_all_trucks(status="active")
    failed_trucks = graph.get_all_trucks(status="failed")
    
    total_packages = 0
    in_transit = 0
    for truck in all_trucks:
        packages = graph.get_truck_packages(truck["truck_id"])
        total_packages += len(packages)
        in_transit += len(packages)
    
    event_stats = simulator.get_event_statistics()
    
    # Display metrics
    with col1:
        st.metric("Total Trucks", len(all_trucks), 
                 delta=f"{len(active_trucks)} active")
    
    with col2:
        st.metric("Active Trucks", len(active_trucks),
                 delta=f"-{len(failed_trucks)}" if failed_trucks else "0")
    
    with col3:
        st.metric("Total Packages", total_packages,
                 delta=f"{in_transit} in transit")
    
    with col4:
        st.metric("Active Events", event_stats["active_events"],
                 delta=f"{event_stats['total_events']} total")
    
    with col5:
        st.metric("Resolved Events", event_stats["resolved_events"])


def display_truck_map(graph: LogisticsGraph):
    """Display interactive map of truck locations"""
    st.subheader("🗺️ Real-time Truck Locations")
    
    trucks = graph.get_all_trucks()
    
    if not trucks:
        st.warning("No trucks in the system")
        return
    
    # Prepare data for map
    truck_data = []
    for truck in trucks:
        truck_data.append({
            "truck_id": truck["truck_id"],
            "lat": truck["current_lat"],
            "lon": truck["current_lon"],
            "status": truck["status"],
            "capacity": truck["capacity"],
            "available_capacity": truck["available_capacity"],
            "direction": truck.get("direction", "N/A")
        })
    
    df = pd.DataFrame(truck_data)
    
    # Create map with color coding by status
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="status",
        size="capacity",
        hover_name="truck_id",
        hover_data=["direction", "available_capacity"],
        color_discrete_map={
            "active": "green",
            "failed": "red",
            "maintenance": "orange"
        },
        zoom=3,
        height=500
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_truck_table(graph: LogisticsGraph):
    """Display detailed truck information table"""
    st.subheader("📋 Truck Fleet Status")
    
    trucks = graph.get_all_trucks()
    
    if not trucks:
        st.warning("No trucks in the system")
        return
    
    # Prepare data
    truck_data = []
    for truck in trucks:
        packages = graph.get_truck_packages(truck["truck_id"])
        truck_data.append({
            "Truck ID": truck["truck_id"],
            "Status": truck["status"],
            "Direction": truck.get("direction", "N/A"),
            "Capacity (kg)": f"{truck['capacity']:.0f}",
            "Available (kg)": f"{truck['available_capacity']:.0f}",
            "Packages": len(packages),
            "Location": f"({truck['current_lat']:.2f}, {truck['current_lon']:.2f})"
        })
    
    df = pd.DataFrame(truck_data)
    
    # Style the dataframe
    def color_status(val):
        if val == "active":
            return "background-color: #90EE90"
        elif val == "failed":
            return "background-color: #FFB6C1"
        else:
            return "background-color: #FFE4B5"
    
    styled_df = df.style.applymap(color_status, subset=["Status"])
    st.dataframe(styled_df, use_container_width=True, height=300)


def display_blast_radius_analysis(graph: LogisticsGraph):
    """Display blast radius analysis for failed trucks"""
    st.subheader("💥 Blast Radius Analysis")
    
    failed_trucks = graph.get_all_trucks(status="failed")
    
    if not failed_trucks:
        st.success("✓ No failed trucks - system is healthy!")
        return
    
    st.warning(f"⚠️ {len(failed_trucks)} truck(s) currently failed")
    
    for truck in failed_trucks:
        with st.expander(f"🚨 {truck['truck_id']} - Impact Analysis"):
            blast_radius = calculate_blast_radius(graph, truck["truck_id"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Affected Deliveries", blast_radius["affected_deliveries"])
                st.metric("Affected Customers", blast_radius["affected_customers"])
                st.metric("Estimated Delay", f"{blast_radius['estimated_delay_hours']:.1f} hours")
            
            with col2:
                st.metric("SLA Penalty per Package", 
                         f"${blast_radius['sla_penalty_per_package']:.2f}")
                st.metric("Total SLA Penalty", 
                         f"${blast_radius['total_sla_penalty']:.2f}",
                         delta=f"-${blast_radius['total_sla_penalty']:.2f}",
                         delta_color="inverse")
            
            st.info(blast_radius["impact_summary"])
            
            # Show affected packages
            packages = graph.get_truck_packages(truck["truck_id"])
            if packages:
                st.markdown("**Affected Packages:**")
                pkg_ids = [pkg["package_id"] for pkg in packages]
                st.write(", ".join(pkg_ids))


def display_event_log(simulator: DisruptionSimulator):
    """Display disruption event log"""
    st.subheader("📜 Disruption Event Log")
    
    events = simulator.events_log
    
    if not events:
        st.info("No disruption events recorded")
        return
    
    # Show latest events first
    events_reversed = list(reversed(events[-20:]))  # Last 20 events
    
    for event in events_reversed:
        status_icon = "✅" if event.resolved else "🔴"
        severity_class = f"alert-{event.severity}"
        
        st.markdown(f"""
        <div class="metric-card">
            {status_icon} <span class="{severity_class}">[{event.severity.upper()}]</span>
            {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {event.description}
        </div>
        """, unsafe_allow_html=True)


def display_disruption_controls(graph: LogisticsGraph, simulator: DisruptionSimulator, 
                               agent: AutonomousReroutingAgent):
    """Display controls for simulating disruptions"""
    st.sidebar.header("🎮 Disruption Controls")
    
    # Manual disruption injection
    st.sidebar.subheader("Inject Chaos Event")
    
    event_type = st.sidebar.selectbox(
        "Event Type",
        ["Truck Failure", "Route Blockage"]
    )
    
    if event_type == "Truck Failure":
        active_trucks = graph.get_all_trucks(status="active")
        if active_trucks:
            truck_ids = [t["truck_id"] for t in active_trucks]
            selected_truck = st.sidebar.selectbox("Select Truck", ["Random"] + truck_ids)
            
            if st.sidebar.button("💥 Inject Failure"):
                truck_id = None if selected_truck == "Random" else selected_truck
                event = simulator.inject_truck_failure(truck_id)
                
                if event:
                    st.sidebar.success(f"Injected: {event.description}")
                    
                    # Automatically trigger rerouting
                    with st.spinner("Running autonomous rerouting..."):
                        result = agent.handle_truck_failure(event.entity_id)
                        if result["status"] == "completed":
                            st.sidebar.success(f"✓ Rerouted {len(result['rerouting_plan'])} packages")
                    
                    st.rerun()
        else:
            st.sidebar.warning("No active trucks available")
    
    else:  # Route Blockage
        if st.sidebar.button("💥 Inject Blockage"):
            event = simulator.inject_route_blockage()
            st.sidebar.success(f"Injected: {event.description}")
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Statistics
    stats = simulator.get_event_statistics()
    agent_stats = agent.get_rerouting_statistics()
    
    st.sidebar.subheader("📊 Statistics")
    st.sidebar.metric("Total Events", stats["total_events"])
    st.sidebar.metric("Active Events", stats["active_events"])
    st.sidebar.metric("Rerouting Operations", agent_stats["total_rerouting_operations"])
    st.sidebar.metric("Packages Rerouted", agent_stats["total_packages_rerouted"])


def display_capacity_chart(graph: LogisticsGraph):
    """Display truck capacity utilization chart"""
    st.subheader("📊 Fleet Capacity Utilization")
    
    trucks = graph.get_all_trucks()
    
    if not trucks:
        st.warning("No trucks in the system")
        return
    
    truck_data = []
    for truck in trucks:
        utilization = ((truck["capacity"] - truck["available_capacity"]) / truck["capacity"]) * 100
        truck_data.append({
            "Truck": truck["truck_id"],
            "Utilization %": utilization,
            "Status": truck["status"]
        })
    
    df = pd.DataFrame(truck_data)
    
    fig = px.bar(
        df,
        x="Truck",
        y="Utilization %",
        color="Status",
        color_discrete_map={
            "active": "green",
            "failed": "red",
            "maintenance": "orange"
        },
        title="Truck Capacity Utilization"
    )
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main dashboard function"""
    display_header()
    
    # Initialize connections
    graph = get_graph_connection()
    
    if not graph:
        st.error("❌ Failed to connect to Neo4j database. Please check your configuration.")
        st.info("Make sure Neo4j is running and the connection details in config.py are correct.")
        return
    
    # Initialize simulator and agent
    if "simulator" not in st.session_state:
        st.session_state.simulator = DisruptionSimulator(graph)
    
    if "agent" not in st.session_state:
        st.session_state.agent = AutonomousReroutingAgent(graph)
    
    simulator = st.session_state.simulator
    agent = st.session_state.agent
    
    # Sidebar controls
    display_disruption_controls(graph, simulator, agent)
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=False)
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Main content
    display_metrics(graph, simulator)
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_truck_map(graph)
        display_capacity_chart(graph)
    
    with col2:
        display_blast_radius_analysis(graph)
    
    st.markdown("---")
    
    display_truck_table(graph)
    
    st.markdown("---")
    
    display_event_log(simulator)
    
    # Footer
    st.markdown("---")
    st.markdown("**Logistics-Lattice** - Agentic Supply Chain Digital Twin | Powered by Neo4j, LangGraph & Streamlit")


if __name__ == "__main__":
    main()
