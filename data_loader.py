"""
Data Loader - Initialize the graph with sample logistics data
"""

import random
from graph_model import LogisticsGraph


class SampleDataLoader:
    """Load sample data into the logistics graph"""
    
    # Sample locations (lat, lon) for demonstration
    WAREHOUSES = [
        {"id": "WH-001", "name": "North Distribution Center", "lat": 40.7128, "lon": -74.0060, "capacity": 10000},
        {"id": "WH-002", "name": "South Distribution Center", "lat": 34.0522, "lon": -118.2437, "capacity": 8000},
        {"id": "WH-003", "name": "East Distribution Center", "lat": 42.3601, "lon": -71.0589, "capacity": 12000},
        {"id": "WH-004", "name": "West Distribution Center", "lat": 37.7749, "lon": -122.4194, "capacity": 9000},
    ]
    
    CUSTOMERS = [
        {"id": "CUST-001", "name": "ABC Electronics", "lat": 40.7580, "lon": -73.9855, "sla_hours": 24},
        {"id": "CUST-002", "name": "XYZ Retail", "lat": 34.0522, "lon": -118.2437, "sla_hours": 48},
        {"id": "CUST-003", "name": "Global Manufacturing", "lat": 41.8781, "lon": -87.6298, "sla_hours": 72},
        {"id": "CUST-004", "name": "Tech Solutions Inc", "lat": 37.7749, "lon": -122.4194, "sla_hours": 24},
        {"id": "CUST-005", "name": "Midwest Distribution", "lat": 39.7392, "lon": -104.9903, "sla_hours": 48},
        {"id": "CUST-006", "name": "East Coast Logistics", "lat": 42.3601, "lon": -71.0589, "sla_hours": 36},
        {"id": "CUST-007", "name": "Pacific Traders", "lat": 47.6062, "lon": -122.3321, "sla_hours": 48},
        {"id": "CUST-008", "name": "Southern Supply Co", "lat": 33.7490, "lon": -84.3880, "sla_hours": 24},
    ]
    
    ROUTE_POINTS = [
        {"id": "RP-001", "name": "Interstate Junction 95", "lat": 40.0, "lon": -74.0, "type": "highway"},
        {"id": "RP-002", "name": "Highway Rest Stop A", "lat": 39.0, "lon": -75.0, "type": "rest_stop"},
        {"id": "RP-003", "name": "Bridge Checkpoint", "lat": 38.0, "lon": -76.0, "type": "checkpoint"},
        {"id": "RP-004", "name": "Mountain Pass", "lat": 37.5, "lon": -119.0, "type": "checkpoint"},
        {"id": "RP-005", "name": "Desert Highway", "lat": 35.0, "lon": -115.0, "type": "highway"},
    ]
    
    DIRECTIONS = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]
    
    def __init__(self, graph: LogisticsGraph):
        self.graph = graph
    
    def load_all_sample_data(self, num_trucks: int = 10, num_packages: int = 30):
        """Load all sample data into the graph"""
        print("\n🔧 Loading sample data...")
        
        # Clear existing data
        confirm = input("This will clear all existing data. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborted.")
            return
        
        self.graph.clear_database()
        
        # Load entities
        self.load_warehouses()
        self.load_customers()
        self.load_route_points()
        self.load_trucks(num_trucks)
        self.load_packages(num_packages)
        
        print("\n✓ Sample data loaded successfully!")
        self._print_summary()
    
    def load_warehouses(self):
        """Load warehouse nodes"""
        print("\n📦 Loading warehouses...")
        for wh in self.WAREHOUSES:
            self.graph.create_warehouse(
                warehouse_id=wh["id"],
                name=wh["name"],
                lat=wh["lat"],
                lon=wh["lon"],
                capacity=wh["capacity"]
            )
        print(f"   ✓ Loaded {len(self.WAREHOUSES)} warehouses")
    
    def load_customers(self):
        """Load customer nodes"""
        print("\n👥 Loading customers...")
        for cust in self.CUSTOMERS:
            self.graph.create_customer(
                customer_id=cust["id"],
                name=cust["name"],
                lat=cust["lat"],
                lon=cust["lon"],
                sla_hours=cust["sla_hours"]
            )
        print(f"   ✓ Loaded {len(self.CUSTOMERS)} customers")
    
    def load_route_points(self):
        """Load route point nodes"""
        print("\n🛣️  Loading route points...")
        for rp in self.ROUTE_POINTS:
            self.graph.create_route_point(
                point_id=rp["id"],
                name=rp["name"],
                lat=rp["lat"],
                lon=rp["lon"],
                point_type=rp["type"]
            )
        print(f"   ✓ Loaded {len(self.ROUTE_POINTS)} route points")
    
    def load_trucks(self, num_trucks: int = 10):
        """Load truck nodes with random locations"""
        print(f"\n🚚 Loading {num_trucks} trucks...")
        
        for i in range(1, num_trucks + 1):
            truck_id = f"TRUCK-{i:03d}"
            
            # Random location within US bounds (roughly)
            lat = random.uniform(30.0, 45.0)
            lon = random.uniform(-125.0, -70.0)
            
            # Random capacity between 1000-5000 kg
            capacity = random.uniform(1000, 5000)
            
            # Random direction
            direction = random.choice(self.DIRECTIONS)
            
            self.graph.create_truck(
                truck_id=truck_id,
                capacity=capacity,
                current_lat=lat,
                current_lon=lon,
                status="active",
                direction=direction
            )
        
        print(f"   ✓ Loaded {num_trucks} trucks")
    
    def load_packages(self, num_packages: int = 30):
        """Load package nodes and assign them to trucks and customers"""
        print(f"\n📦 Loading {num_packages} packages...")
        
        trucks = self.graph.get_all_trucks(status="active")
        
        if not trucks:
            print("   ⚠️  No active trucks available. Load trucks first.")
            return
        
        packages_created = 0
        
        for i in range(1, num_packages + 1):
            package_id = f"PKG-{i:04d}"
            
            # Random weight between 50-500 kg
            weight = random.uniform(50, 500)
            
            # Random customer
            customer = random.choice(self.CUSTOMERS)
            
            # Create package
            self.graph.create_package(
                package_id=package_id,
                weight=weight,
                destination_lat=customer["lat"],
                destination_lon=customer["lon"],
                status="pending",
                priority=random.choice(["normal", "high", "urgent"])
            )
            
            # Assign to customer
            self.graph.assign_package_destination(package_id, customer["id"])
            
            # Assign to a random truck with available capacity
            available_trucks = [t for t in trucks if t["available_capacity"] >= weight]
            
            if available_trucks:
                truck = random.choice(available_trucks)
                self.graph.assign_package_to_truck(truck["truck_id"], package_id)
                
                # Update local truck capacity tracking
                for t in trucks:
                    if t["truck_id"] == truck["truck_id"]:
                        t["available_capacity"] -= weight
                        break
                
                packages_created += 1
            else:
                print(f"   ⚠️  Package {package_id} not assigned - no trucks with capacity")
        
        print(f"   ✓ Loaded and assigned {packages_created} packages")
    
    def _print_summary(self):
        """Print a summary of loaded data"""
        print("\n" + "="*60)
        print("  DATA LOADING SUMMARY")
        print("="*60)
        
        trucks = self.graph.get_all_trucks()
        active_trucks = self.graph.get_all_trucks(status="active")
        
        print(f"Warehouses:  {len(self.WAREHOUSES)}")
        print(f"Customers:   {len(self.CUSTOMERS)}")
        print(f"Route Points: {len(self.ROUTE_POINTS)}")
        print(f"Trucks:      {len(trucks)} (Active: {len(active_trucks)})")
        
        # Count packages per truck
        total_packages = 0
        for truck in trucks:
            packages = self.graph.get_truck_packages(truck["truck_id"])
            total_packages += len(packages)
        
        print(f"Packages:    {total_packages}")
        print("="*60 + "\n")
    
    def add_sample_route_associations(self):
        """Add LOCATED_AT relationships between trucks and route points"""
        print("\n🔗 Creating route associations...")
        
        trucks = self.graph.get_all_trucks()
        
        for truck in trucks[:3]:  # Associate first 3 trucks with route points
            rp = random.choice(self.ROUTE_POINTS)
            self.graph.locate_truck_at_point(truck["truck_id"], rp["id"])
        
        print(f"   ✓ Created route associations")


def quick_load(num_trucks: int = 10, num_packages: int = 30):
    """Quick function to load sample data"""
    graph = LogisticsGraph()
    
    if not graph.connect():
        print("❌ Failed to connect to Neo4j")
        return False
    
    try:
        graph.initialize_schema()
        loader = SampleDataLoader(graph)
        loader.load_all_sample_data(num_trucks, num_packages)
        return True
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    finally:
        graph.close()


if __name__ == "__main__":
    print("=== Sample Data Loader for Logistics-Lattice ===\n")
    
    graph = LogisticsGraph()
    
    if graph.connect():
        graph.initialize_schema()
        loader = SampleDataLoader(graph)
        loader.load_all_sample_data(num_trucks=10, num_packages=30)
        loader.add_sample_route_associations()
        graph.close()
