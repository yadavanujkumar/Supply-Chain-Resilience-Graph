"""
Disruption Simulator - Chaos Events Injection
Simulates real-world logistics disruptions
"""

import random
import time
from typing import Dict, List, Optional
from datetime import datetime
from graph_model import LogisticsGraph


class DisruptionEvent:
    """Represents a chaos event in the logistics network"""
    
    def __init__(self, event_type: str, entity_id: str, severity: str, 
                 description: str, timestamp: Optional[datetime] = None):
        self.event_type = event_type  # truck_failure, route_blocked, warehouse_delay
        self.entity_id = entity_id
        self.severity = severity  # low, medium, high, critical
        self.description = description
        self.timestamp = timestamp or datetime.now()
        self.resolved = False
    
    def __str__(self):
        status = "RESOLVED" if self.resolved else "ACTIVE"
        return f"[{status}] {self.timestamp.strftime('%H:%M:%S')} - {self.severity.upper()}: {self.description}"


class DisruptionSimulator:
    """Simulates and injects chaos events into the logistics network"""
    
    TRUCK_FAILURES = [
        "Engine Failure",
        "Tire Blowout",
        "Transmission Problem",
        "Electrical System Failure",
        "Brake Malfunction",
        "Fuel System Issue",
        "Overheating",
    ]
    
    ROUTE_ISSUES = [
        "Road Flooded",
        "Bridge Closed",
        "Traffic Accident",
        "Road Construction",
        "Severe Weather",
        "Road Collapse",
    ]
    
    def __init__(self, graph: LogisticsGraph):
        self.graph = graph
        self.events_log: List[DisruptionEvent] = []
        self.active_events: List[DisruptionEvent] = []
    
    def inject_truck_failure(self, truck_id: Optional[str] = None) -> DisruptionEvent:
        """Inject a truck failure event"""
        # If no truck specified, pick a random active truck
        if not truck_id:
            trucks = self.graph.get_all_trucks(status="active")
            if not trucks:
                return None
            truck_id = random.choice(trucks)["truck_id"]
        
        # Create failure event
        failure_type = random.choice(self.TRUCK_FAILURES)
        severity = random.choice(["medium", "high", "critical"])
        
        event = DisruptionEvent(
            event_type="truck_failure",
            entity_id=truck_id,
            severity=severity,
            description=f"Truck {truck_id}: {failure_type}"
        )
        
        # Update graph to reflect failure
        self.graph.update_truck_status(truck_id, "failed")
        
        # Log event
        self.events_log.append(event)
        self.active_events.append(event)
        
        print(f"🚨 DISRUPTION: {event}")
        return event
    
    def inject_route_blockage(self, point_id: Optional[str] = None) -> DisruptionEvent:
        """Inject a route blockage event"""
        if not point_id:
            # In a real system, we'd query for route points
            point_id = f"ROUTE-{random.randint(1, 100)}"
        
        issue_type = random.choice(self.ROUTE_ISSUES)
        severity = random.choice(["low", "medium", "high"])
        
        event = DisruptionEvent(
            event_type="route_blocked",
            entity_id=point_id,
            severity=severity,
            description=f"Route {point_id}: {issue_type}"
        )
        
        self.events_log.append(event)
        self.active_events.append(event)
        
        print(f"🚨 DISRUPTION: {event}")
        return event
    
    def inject_random_chaos(self, probability: float = 0.3) -> Optional[DisruptionEvent]:
        """
        Randomly inject a chaos event based on probability
        
        Args:
            probability: Chance of event occurring (0.0 to 1.0)
        
        Returns:
            DisruptionEvent if one was created, None otherwise
        """
        if random.random() < probability:
            event_type = random.choice(["truck_failure", "route_blocked"])
            
            if event_type == "truck_failure":
                return self.inject_truck_failure()
            else:
                return self.inject_route_blockage()
        
        return None
    
    def resolve_event(self, event: DisruptionEvent):
        """Mark an event as resolved"""
        event.resolved = True
        if event in self.active_events:
            self.active_events.remove(event)
        print(f"✓ RESOLVED: {event.description}")
    
    def get_active_events(self) -> List[DisruptionEvent]:
        """Get all currently active disruption events"""
        return self.active_events
    
    def get_events_by_type(self, event_type: str) -> List[DisruptionEvent]:
        """Get events filtered by type"""
        return [e for e in self.events_log if e.event_type == event_type]
    
    def get_event_statistics(self) -> Dict:
        """Get statistics about disruption events"""
        total = len(self.events_log)
        active = len(self.active_events)
        resolved = total - active
        
        by_type = {}
        by_severity = {}
        
        for event in self.events_log:
            by_type[event.event_type] = by_type.get(event.event_type, 0) + 1
            by_severity[event.severity] = by_severity.get(event.severity, 0) + 1
        
        return {
            "total_events": total,
            "active_events": active,
            "resolved_events": resolved,
            "by_type": by_type,
            "by_severity": by_severity
        }
    
    def start_continuous_simulation(self, interval: int = 30, 
                                    chaos_probability: float = 0.2,
                                    duration: Optional[int] = None):
        """
        Start continuous chaos simulation
        
        Args:
            interval: Seconds between chaos injection attempts
            chaos_probability: Probability of event per interval
            duration: Total duration in seconds (None for infinite)
        """
        print(f"🎯 Starting chaos simulation (interval={interval}s, probability={chaos_probability})")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                iteration += 1
                
                # Check if duration exceeded
                if duration and (time.time() - start_time) > duration:
                    break
                
                # Inject random chaos
                event = self.inject_random_chaos(probability=chaos_probability)
                
                if event:
                    print(f"  Iteration {iteration}: Event injected")
                else:
                    print(f"  Iteration {iteration}: No event")
                
                # Wait for next iteration
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n⏸️  Chaos simulation stopped by user")
        
        print(f"📊 Simulation complete: {iteration} iterations")
        print(f"📊 Statistics: {self.get_event_statistics()}")


class ChaosEventGenerator:
    """Generate realistic chaos events with patterns"""
    
    @staticmethod
    def generate_cascading_failures(graph: LogisticsGraph, 
                                    initial_truck_id: str,
                                    cascade_probability: float = 0.4) -> List[DisruptionEvent]:
        """
        Generate cascading failures where one disruption leads to others
        """
        simulator = DisruptionSimulator(graph)
        events = []
        
        # Initial failure
        event = simulator.inject_truck_failure(initial_truck_id)
        if event:
            events.append(event)
        
        # Get nearby trucks that might be affected
        truck = graph.get_truck(initial_truck_id)
        if truck:
            nearby_trucks = graph.find_nearest_available_trucks(
                truck["current_lat"], 
                truck["current_lon"],
                min_capacity=0,
                limit=3
            )
            
            # Random cascading failures
            for nearby in nearby_trucks:
                if random.random() < cascade_probability:
                    cascade_event = simulator.inject_truck_failure(
                        nearby["truck"]["truck_id"]
                    )
                    if cascade_event:
                        events.append(cascade_event)
        
        return events
    
    @staticmethod
    def generate_weather_event(graph: LogisticsGraph, 
                               affected_region: tuple) -> List[DisruptionEvent]:
        """
        Generate weather-related disruptions affecting a region
        
        Args:
            affected_region: (center_lat, center_lon, radius_degrees)
        
        Note: Uses simple Euclidean distance for regional weather patterns.
        For large geographic areas, consider using Haversine formula.
        """
        simulator = DisruptionSimulator(graph)
        events = []
        
        center_lat, center_lon, radius = affected_region
        
        # Find all trucks in the affected region
        all_trucks = graph.get_all_trucks(status="active")
        
        for truck in all_trucks:
            lat_diff = abs(truck["current_lat"] - center_lat)
            lon_diff = abs(truck["current_lon"] - center_lon)
            # Simple Euclidean distance (approximation for regional areas)
            distance = (lat_diff**2 + lon_diff**2)**0.5
            
            if distance <= radius:
                # Truck is in affected area
                event = simulator.inject_truck_failure(truck["truck_id"])
                if event:
                    event.description = f"Weather Impact - {event.description}"
                    events.append(event)
        
        return events


if __name__ == "__main__":
    # Test the simulator
    from graph_model import LogisticsGraph
    
    graph = LogisticsGraph()
    if graph.connect():
        simulator = DisruptionSimulator(graph)
        
        # Test individual events
        print("\n=== Testing Disruption Simulator ===\n")
        
        # Note: These will only work if there are trucks in the database
        # simulator.inject_truck_failure()
        # simulator.inject_route_blockage()
        
        print(f"\nStatistics: {simulator.get_event_statistics()}")
        
        graph.close()
