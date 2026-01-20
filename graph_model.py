"""
Graph Data Model for Logistics-Lattice
Defines the Neo4j schema for the supply chain digital twin
"""

from neo4j import GraphDatabase
from typing import Dict, List, Optional
import config


class LogisticsGraph:
    """Manages the Neo4j graph database for the logistics network"""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        self.uri = uri or config.NEO4J_URI
        self.user = user or config.NEO4J_USER
        self.password = password or config.NEO4J_PASSWORD
        self.driver = None
        
    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            print(f"✓ Connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Neo4j: {e}")
            return False
    
    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
            print("✓ Closed Neo4j connection")
    
    def initialize_schema(self):
        """Create the graph schema with constraints and indexes"""
        with self.driver.session() as session:
            # Create constraints for unique IDs
            constraints = [
                "CREATE CONSTRAINT truck_id IF NOT EXISTS FOR (t:Truck) REQUIRE t.truck_id IS UNIQUE",
                "CREATE CONSTRAINT package_id IF NOT EXISTS FOR (p:Package) REQUIRE p.package_id IS UNIQUE",
                "CREATE CONSTRAINT warehouse_id IF NOT EXISTS FOR (w:Warehouse) REQUIRE w.warehouse_id IS UNIQUE",
                "CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE",
                "CREATE CONSTRAINT route_point_id IF NOT EXISTS FOR (r:RoutePoint) REQUIRE r.point_id IS UNIQUE",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"Warning: {e}")
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX truck_status IF NOT EXISTS FOR (t:Truck) ON (t.status)",
                "CREATE INDEX package_status IF NOT EXISTS FOR (p:Package) ON (p.status)",
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"Warning: {e}")
            
            print("✓ Schema initialized")
    
    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")
    
    # === CREATE NODES ===
    
    def create_truck(self, truck_id: str, capacity: float, current_lat: float, 
                     current_lon: float, status: str = "active", 
                     direction: Optional[str] = None) -> Dict:
        """Create a Truck node"""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (t:Truck {truck_id: $truck_id})
                SET t.capacity = $capacity,
                    t.available_capacity = $capacity,
                    t.current_lat = $current_lat,
                    t.current_lon = $current_lon,
                    t.status = $status,
                    t.direction = $direction
                RETURN t
            """, truck_id=truck_id, capacity=capacity, current_lat=current_lat,
                current_lon=current_lon, status=status, direction=direction)
            return result.single()
    
    def create_package(self, package_id: str, weight: float, destination_lat: float,
                       destination_lon: float, status: str = "pending",
                       priority: str = "normal", expected_eta: Optional[str] = None) -> Dict:
        """Create a Package node"""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (p:Package {package_id: $package_id})
                SET p.weight = $weight,
                    p.destination_lat = $destination_lat,
                    p.destination_lon = $destination_lon,
                    p.status = $status,
                    p.priority = $priority,
                    p.expected_eta = $expected_eta
                RETURN p
            """, package_id=package_id, weight=weight, destination_lat=destination_lat,
                destination_lon=destination_lon, status=status, priority=priority,
                expected_eta=expected_eta)
            return result.single()
    
    def create_warehouse(self, warehouse_id: str, name: str, lat: float, lon: float,
                         capacity: float) -> Dict:
        """Create a Warehouse node"""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (w:Warehouse {warehouse_id: $warehouse_id})
                SET w.name = $name,
                    w.lat = $lat,
                    w.lon = $lon,
                    w.capacity = $capacity
                RETURN w
            """, warehouse_id=warehouse_id, name=name, lat=lat, lon=lon, capacity=capacity)
            return result.single()
    
    def create_customer(self, customer_id: str, name: str, lat: float, lon: float,
                        sla_hours: float = 24.0) -> Dict:
        """Create a Customer node"""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (c:Customer {customer_id: $customer_id})
                SET c.name = $name,
                    c.lat = $lat,
                    c.lon = $lon,
                    c.sla_hours = $sla_hours
                RETURN c
            """, customer_id=customer_id, name=name, lat=lat, lon=lon, sla_hours=sla_hours)
            return result.single()
    
    def create_route_point(self, point_id: str, name: str, lat: float, lon: float,
                          point_type: str = "checkpoint") -> Dict:
        """Create a RoutePoint node"""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (r:RoutePoint {point_id: $point_id})
                SET r.name = $name,
                    r.lat = $lat,
                    r.lon = $lon,
                    r.type = $point_type,
                    r.status = 'open'
                RETURN r
            """, point_id=point_id, name=name, lat=lat, lon=lon, point_type=point_type)
            return result.single()
    
    # === CREATE RELATIONSHIPS ===
    
    def assign_package_to_truck(self, truck_id: str, package_id: str) -> bool:
        """Create CARRYING relationship between Truck and Package"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Truck {truck_id: $truck_id})
                MATCH (p:Package {package_id: $package_id})
                MERGE (t)-[r:CARRYING]->(p)
                SET t.available_capacity = t.available_capacity - p.weight,
                    p.status = 'in_transit'
                RETURN r
            """, truck_id=truck_id, package_id=package_id)
            return result.single() is not None
    
    def locate_truck_at_point(self, truck_id: str, point_id: str) -> bool:
        """Create LOCATED_AT relationship between Truck and RoutePoint"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Truck {truck_id: $truck_id})
                MATCH (r:RoutePoint {point_id: $point_id})
                MERGE (t)-[rel:LOCATED_AT]->(r)
                RETURN rel
            """, truck_id=truck_id, point_id=point_id)
            return result.single() is not None
    
    def assign_package_destination(self, package_id: str, customer_id: str) -> bool:
        """Create DESTINED_FOR relationship between Package and Customer"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Package {package_id: $package_id})
                MATCH (c:Customer {customer_id: $customer_id})
                MERGE (p)-[r:DESTINED_FOR]->(c)
                RETURN r
            """, package_id=package_id, customer_id=customer_id)
            return result.single() is not None
    
    # === QUERY OPERATIONS ===
    
    def get_truck(self, truck_id: str) -> Optional[Dict]:
        """Get truck details by ID"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Truck {truck_id: $truck_id})
                RETURN t
            """, truck_id=truck_id)
            record = result.single()
            return dict(record["t"]) if record else None
    
    def get_all_trucks(self, status: Optional[str] = None) -> List[Dict]:
        """Get all trucks, optionally filtered by status"""
        with self.driver.session() as session:
            if status:
                result = session.run("""
                    MATCH (t:Truck {status: $status})
                    RETURN t
                """, status=status)
            else:
                result = session.run("MATCH (t:Truck) RETURN t")
            
            return [dict(record["t"]) for record in result]
    
    def get_truck_packages(self, truck_id: str) -> List[Dict]:
        """Get all packages carried by a truck"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Truck {truck_id: $truck_id})-[:CARRYING]->(p:Package)
                RETURN p
            """, truck_id=truck_id)
            return [dict(record["p"]) for record in result]
    
    def find_nearest_available_trucks(self, lat: float, lon: float, 
                                     min_capacity: float, direction: Optional[str] = None,
                                     limit: int = 5) -> List[Dict]:
        """
        Find nearest available trucks with sufficient capacity
        Uses Euclidean distance for geospatial calculations
        
        Note: For more accurate geographic distance over large areas,
        consider using Haversine formula or a geospatial library.
        Current implementation is optimized for speed and works well
        for regional logistics networks.
        """
        with self.driver.session() as session:
            if direction:
                result = session.run("""
                    MATCH (t:Truck)
                    WHERE t.status = 'active' 
                      AND t.available_capacity >= $min_capacity
                      AND t.direction = $direction
                    WITH t, 
                         sqrt(power(t.current_lat - $lat, 2) + power(t.current_lon - $lon, 2)) AS distance
                    RETURN t, distance
                    ORDER BY distance
                    LIMIT $limit
                """, lat=lat, lon=lon, min_capacity=min_capacity, direction=direction, limit=limit)
            else:
                result = session.run("""
                    MATCH (t:Truck)
                    WHERE t.status = 'active' 
                      AND t.available_capacity >= $min_capacity
                    WITH t, 
                         sqrt(power(t.current_lat - $lat, 2) + power(t.current_lon - $lon, 2)) AS distance
                    RETURN t, distance
                    ORDER BY distance
                    LIMIT $limit
                """, lat=lat, lon=lon, min_capacity=min_capacity, limit=limit)
            
            return [{"truck": dict(record["t"]), "distance": record["distance"]} 
                    for record in result]
    
    def transfer_package(self, package_id: str, from_truck_id: str, to_truck_id: str) -> bool:
        """Transfer a package from one truck to another (atomic transaction)"""
        with self.driver.session() as session:
            # Use a single transaction to ensure atomicity
            try:
                result = session.run("""
                    MATCH (from:Truck {truck_id: $from_truck_id})-[r:CARRYING]->(p:Package {package_id: $package_id})
                    MATCH (to:Truck {truck_id: $to_truck_id})
                    WHERE to.available_capacity >= p.weight
                    WITH from, to, p, r
                    DELETE r
                    CREATE (to)-[:CARRYING]->(p)
                    SET from.available_capacity = from.available_capacity + p.weight,
                        to.available_capacity = to.available_capacity - p.weight
                    RETURN p
                """, package_id=package_id, from_truck_id=from_truck_id, to_truck_id=to_truck_id)
                return result.single() is not None
            except Exception as e:
                print(f"Error transferring package {package_id}: {e}")
                return False
    
    def update_truck_status(self, truck_id: str, status: str) -> bool:
        """Update truck status (active, failed, maintenance)"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Truck {truck_id: $truck_id})
                SET t.status = $status
                RETURN t
            """, truck_id=truck_id, status=status)
            return result.single() is not None
    
    def update_truck_location(self, truck_id: str, lat: float, lon: float) -> bool:
        """Update truck's current location"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Truck {truck_id: $truck_id})
                SET t.current_lat = $lat,
                    t.current_lon = $lon
                RETURN t
            """, truck_id=truck_id, lat=lat, lon=lon)
            return result.single() is not None
    
    def get_impact_analysis(self, truck_id: str) -> Dict:
        """
        Calculate the blast radius of a truck failure
        Returns affected packages, customers, and estimated penalties
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Truck {truck_id: $truck_id})-[:CARRYING]->(p:Package)-[:DESTINED_FOR]->(c:Customer)
                RETURN count(p) as affected_packages,
                       count(DISTINCT c) as affected_customers,
                       collect(DISTINCT c.customer_id) as customer_ids,
                       collect(p.package_id) as package_ids,
                       sum(p.weight) as total_weight
            """, truck_id=truck_id)
            
            record = result.single()
            if record:
                return {
                    "affected_packages": record["affected_packages"],
                    "affected_customers": record["affected_customers"],
                    "customer_ids": record["customer_ids"],
                    "package_ids": record["package_ids"],
                    "total_weight": record["total_weight"]
                }
            return {
                "affected_packages": 0,
                "affected_customers": 0,
                "customer_ids": [],
                "package_ids": [],
                "total_weight": 0
            }


if __name__ == "__main__":
    # Test connection
    graph = LogisticsGraph()
    if graph.connect():
        graph.initialize_schema()
        print("✓ Graph model ready")
        graph.close()
