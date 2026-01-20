"""
Main Application - Logistics-Lattice Entry Point
Orchestrates all components of the digital twin
"""

import sys
import argparse
from graph_model import LogisticsGraph
from data_loader import SampleDataLoader
from disruption_simulator import DisruptionSimulator
from rerouting_agent import AutonomousReroutingAgent


def setup_database():
    """Initialize the database schema"""
    print("\n🔧 Setting up database...")
    graph = LogisticsGraph()
    
    if not graph.connect():
        print("❌ Failed to connect to Neo4j")
        return False
    
    try:
        graph.initialize_schema()
        print("✓ Database schema initialized")
        graph.close()
        return True
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        graph.close()
        return False


def load_sample_data(num_trucks: int = 10, num_packages: int = 30):
    """Load sample data into the database"""
    print("\n📦 Loading sample data...")
    graph = LogisticsGraph()
    
    if not graph.connect():
        print("❌ Failed to connect to Neo4j")
        return False
    
    try:
        graph.initialize_schema()
        loader = SampleDataLoader(graph)
        loader.load_all_sample_data(num_trucks, num_packages)
        loader.add_sample_route_associations()
        graph.close()
        return True
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        graph.close()
        return False


def run_simulation(duration: int = 60):
    """Run the chaos simulation"""
    print("\n🎯 Starting chaos simulation...")
    graph = LogisticsGraph()
    
    if not graph.connect():
        print("❌ Failed to connect to Neo4j")
        return False
    
    try:
        simulator = DisruptionSimulator(graph)
        agent = AutonomousReroutingAgent(graph)
        
        print("✓ Simulator and agent initialized")
        print(f"✓ Running for {duration} seconds...")
        print("\nPress Ctrl+C to stop\n")
        
        # Run simulation
        simulator.start_continuous_simulation(
            interval=10,
            chaos_probability=0.3,
            duration=duration
        )
        
        # Print statistics
        print("\n" + "="*60)
        print("  SIMULATION COMPLETE")
        print("="*60)
        
        sim_stats = simulator.get_event_statistics()
        agent_stats = agent.get_rerouting_statistics()
        
        print(f"\nDisruption Events:")
        print(f"  Total: {sim_stats['total_events']}")
        print(f"  Active: {sim_stats['active_events']}")
        print(f"  Resolved: {sim_stats['resolved_events']}")
        
        print(f"\nRerouting Operations:")
        print(f"  Total operations: {agent_stats['total_rerouting_operations']}")
        print(f"  Packages rerouted: {agent_stats['total_packages_rerouted']}")
        print(f"  Avg packages/op: {agent_stats['average_packages_per_operation']:.2f}")
        
        print("\n" + "="*60 + "\n")
        
        graph.close()
        return True
        
    except Exception as e:
        print(f"❌ Error running simulation: {e}")
        graph.close()
        return False


def test_connection():
    """Test the Neo4j connection"""
    print("\n🔌 Testing Neo4j connection...")
    graph = LogisticsGraph()
    
    if graph.connect():
        print("✓ Successfully connected to Neo4j")
        
        # Get some stats
        trucks = graph.get_all_trucks()
        print(f"✓ Found {len(trucks)} trucks in database")
        
        graph.close()
        return True
    else:
        print("❌ Failed to connect to Neo4j")
        print("\nTroubleshooting:")
        print("1. Make sure Neo4j is running")
        print("2. Check your .env file configuration")
        print("3. Verify NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD")
        return False


def run_dashboard():
    """Run the Streamlit dashboard"""
    print("\n🎨 Starting dashboard...")
    print("✓ Dashboard will open in your browser")
    print("✓ Press Ctrl+C to stop\n")
    
    import subprocess
    import shutil
    
    # Check if streamlit is available
    if not shutil.which("streamlit"):
        print("❌ Streamlit not found. Please install with: pip install streamlit")
        return False
    
    try:
        subprocess.run(["streamlit", "run", "dashboard.py"], shell=False, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running dashboard: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏸️  Dashboard stopped")
        return True


def print_usage():
    """Print usage information"""
    print("""
╔════════════════════════════════════════════════════════════╗
║         Logistics-Lattice Digital Twin System              ║
║      Autonomous Supply Chain Resilience Platform           ║
╚════════════════════════════════════════════════════════════╝

Usage:
  python main.py <command> [options]

Commands:
  setup                 Initialize database schema
  load-data            Load sample data (trucks, packages, etc.)
  test                 Test Neo4j connection
  simulate             Run chaos simulation
  dashboard            Launch Streamlit dashboard
  help                 Show this help message

Options:
  --trucks N           Number of trucks to create (default: 10)
  --packages N         Number of packages to create (default: 30)
  --duration N         Simulation duration in seconds (default: 60)

Examples:
  python main.py setup
  python main.py load-data --trucks 15 --packages 50
  python main.py simulate --duration 120
  python main.py dashboard

Setup Instructions:
  1. Install dependencies:     pip install -r requirements.txt
  2. Configure .env:           cp .env.example .env (and edit)
  3. Start Neo4j database
  4. Initialize schema:        python main.py setup
  5. Load sample data:         python main.py load-data
  6. Launch dashboard:         python main.py dashboard
""")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Logistics-Lattice Digital Twin System",
        add_help=False
    )
    
    parser.add_argument("command", nargs="?", default="help",
                       choices=["setup", "load-data", "test", "simulate", "dashboard", "help"])
    parser.add_argument("--trucks", type=int, default=10,
                       help="Number of trucks to create")
    parser.add_argument("--packages", type=int, default=30,
                       help="Number of packages to create")
    parser.add_argument("--duration", type=int, default=60,
                       help="Simulation duration in seconds")
    
    args = parser.parse_args()
    
    if args.command == "help":
        print_usage()
        return 0
    
    elif args.command == "setup":
        success = setup_database()
        return 0 if success else 1
    
    elif args.command == "load-data":
        success = load_sample_data(args.trucks, args.packages)
        return 0 if success else 1
    
    elif args.command == "test":
        success = test_connection()
        return 0 if success else 1
    
    elif args.command == "simulate":
        success = run_simulation(args.duration)
        return 0 if success else 1
    
    elif args.command == "dashboard":
        run_dashboard()
        return 0
    
    else:
        print_usage()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
