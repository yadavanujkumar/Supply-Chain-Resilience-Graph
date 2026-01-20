"""
Autonomous Re-Routing Agent
Uses LangGraph to handle package re-routing when disruptions occur
"""

from typing import Dict, List, Optional, TypedDict
from datetime import datetime, timedelta
import math
from langgraph.graph import StateGraph, END
from graph_model import LogisticsGraph
from disruption_simulator import DisruptionEvent
import config


class ReroutingState(TypedDict):
    """State for the rerouting agent workflow"""
    failed_truck_id: str
    affected_packages: List[str]
    available_trucks: List[Dict]
    rerouting_plan: List[Dict]
    status: str
    message: str


class AutonomousReroutingAgent:
    """
    Autonomous agent that responds to truck failures and reroutes packages
    Uses graph queries and geospatial calculations
    """
    
    def __init__(self, graph: LogisticsGraph):
        self.graph = graph
        self.workflow = self._build_workflow()
        self.rerouting_history: List[Dict] = []
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for rerouting logic"""
        workflow = StateGraph(ReroutingState)
        
        # Define workflow nodes
        workflow.add_node("detect_failure", self._detect_failure)
        workflow.add_node("assess_impact", self._assess_impact)
        workflow.add_node("find_alternatives", self._find_alternatives)
        workflow.add_node("execute_rerouting", self._execute_rerouting)
        workflow.add_node("calculate_eta", self._calculate_eta)
        workflow.add_node("complete", self._complete)
        
        # Define workflow edges
        workflow.set_entry_point("detect_failure")
        workflow.add_edge("detect_failure", "assess_impact")
        workflow.add_edge("assess_impact", "find_alternatives")
        workflow.add_edge("find_alternatives", "execute_rerouting")
        workflow.add_edge("execute_rerouting", "calculate_eta")
        workflow.add_edge("calculate_eta", "complete")
        workflow.add_edge("complete", END)
        
        return workflow.compile()
    
    def _detect_failure(self, state: ReroutingState) -> ReroutingState:
        """Step 1: Detect and validate the truck failure"""
        truck_id = state["failed_truck_id"]
        truck = self.graph.get_truck(truck_id)
        
        if not truck or truck.get("status") != "failed":
            state["status"] = "error"
            state["message"] = f"Truck {truck_id} not found or not in failed state"
            return state
        
        state["status"] = "failure_detected"
        state["message"] = f"Truck {truck_id} failure confirmed"
        return state
    
    def _assess_impact(self, state: ReroutingState) -> ReroutingState:
        """Step 2: Assess the impact of the failure"""
        truck_id = state["failed_truck_id"]
        
        # Get impact analysis from graph
        impact = self.graph.get_impact_analysis(truck_id)
        
        state["affected_packages"] = impact["package_ids"]
        state["status"] = "impact_assessed"
        state["message"] = f"Found {len(impact['package_ids'])} affected packages"
        
        return state
    
    def _find_alternatives(self, state: ReroutingState) -> ReroutingState:
        """Step 3: Find alternative trucks for each package"""
        truck_id = state["failed_truck_id"]
        packages = state["affected_packages"]
        
        if not packages:
            state["status"] = "no_packages"
            state["message"] = "No packages to reroute"
            state["available_trucks"] = []
            return state
        
        # Get failed truck location
        failed_truck = self.graph.get_truck(truck_id)
        truck_lat = failed_truck["current_lat"]
        truck_lon = failed_truck["current_lon"]
        truck_direction = failed_truck.get("direction")
        
        # Get all packages with their details (single query)
        packages_data = self.graph.get_truck_packages(truck_id)
        package_details = [pkg for pkg in packages_data if pkg["package_id"] in packages]
        
        # Find alternative trucks for each package
        available_trucks = []
        for pkg in package_details:
            # Find nearest trucks with capacity
            candidates = self.graph.find_nearest_available_trucks(
                lat=truck_lat,
                lon=truck_lon,
                min_capacity=pkg["weight"],
                direction=truck_direction,
                limit=5
            )
            
            if candidates:
                available_trucks.append({
                    "package_id": pkg["package_id"],
                    "candidates": candidates
                })
        
        state["available_trucks"] = available_trucks
        state["status"] = "alternatives_found"
        state["message"] = f"Found alternative trucks for {len(available_trucks)} packages"
        
        return state
    
    def _execute_rerouting(self, state: ReroutingState) -> ReroutingState:
        """Step 4: Execute the package transfers"""
        failed_truck_id = state["failed_truck_id"]
        available_trucks = state["available_trucks"]
        rerouting_plan = []
        
        for pkg_info in available_trucks:
            package_id = pkg_info["package_id"]
            candidates = pkg_info["candidates"]
            
            if not candidates:
                continue
            
            # Choose the nearest truck
            best_truck = candidates[0]["truck"]
            distance = candidates[0]["distance"]
            
            # Execute transfer in graph
            success = self.graph.transfer_package(
                package_id=package_id,
                from_truck_id=failed_truck_id,
                to_truck_id=best_truck["truck_id"]
            )
            
            if success:
                rerouting_plan.append({
                    "package_id": package_id,
                    "new_truck_id": best_truck["truck_id"],
                    "distance": distance,
                    "timestamp": datetime.now().isoformat()
                })
        
        state["rerouting_plan"] = rerouting_plan
        state["status"] = "rerouting_executed"
        state["message"] = f"Successfully rerouted {len(rerouting_plan)} packages"
        
        return state
    
    def _calculate_eta(self, state: ReroutingState) -> ReroutingState:
        """Step 5: Calculate new ETAs for rerouted packages"""
        rerouting_plan = state["rerouting_plan"]
        
        for plan in rerouting_plan:
            # Get package destination
            package_id = plan["package_id"]
            new_truck_id = plan["new_truck_id"]
            
            # Simple ETA calculation based on distance and speed
            # In reality, this would use Google Maps API
            distance_km = plan["distance"] * 111  # Convert degrees to km (approximate)
            hours = distance_km / config.TRUCK_SPEED_KMH
            
            new_eta = datetime.now() + timedelta(hours=hours)
            plan["estimated_eta"] = new_eta.isoformat()
            plan["delay_hours"] = hours
        
        state["status"] = "eta_calculated"
        state["message"] = "ETAs recalculated for all packages"
        
        return state
    
    def _complete(self, state: ReroutingState) -> ReroutingState:
        """Step 6: Complete the rerouting process"""
        state["status"] = "completed"
        
        # Store in history
        self.rerouting_history.append({
            "timestamp": datetime.now().isoformat(),
            "failed_truck_id": state["failed_truck_id"],
            "packages_rerouted": len(state.get("rerouting_plan", [])),
            "plan": state.get("rerouting_plan", [])
        })
        
        return state
    
    def handle_truck_failure(self, truck_id: str) -> Dict:
        """
        Main entry point: Handle a truck failure event
        
        Args:
            truck_id: ID of the failed truck
        
        Returns:
            Dictionary with rerouting results
        """
        print(f"\n🔄 Starting autonomous rerouting for truck {truck_id}...")
        
        # Initialize state
        initial_state = ReroutingState(
            failed_truck_id=truck_id,
            affected_packages=[],
            available_trucks=[],
            rerouting_plan=[],
            status="initialized",
            message=""
        )
        
        # Run workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            # Print results
            self._print_rerouting_results(final_state)
            
            return final_state
        
        except Exception as e:
            print(f"❌ Error during rerouting: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _print_rerouting_results(self, state: ReroutingState):
        """Print detailed rerouting results"""
        print(f"\n{'='*60}")
        print(f"  REROUTING RESULTS")
        print(f"{'='*60}")
        print(f"Failed Truck: {state['failed_truck_id']}")
        print(f"Status: {state['status']}")
        print(f"Message: {state['message']}")
        print(f"\nPackages Affected: {len(state.get('affected_packages', []))}")
        print(f"Packages Rerouted: {len(state.get('rerouting_plan', []))}")
        
        if state.get("rerouting_plan"):
            print(f"\nRerouting Plan:")
            for i, plan in enumerate(state["rerouting_plan"], 1):
                print(f"  {i}. Package {plan['package_id']}")
                print(f"     → New Truck: {plan['new_truck_id']}")
                print(f"     → Distance: {plan['distance']:.4f} degrees")
                if "estimated_eta" in plan:
                    print(f"     → New ETA: {plan['estimated_eta']}")
                    print(f"     → Delay: {plan.get('delay_hours', 0):.2f} hours")
        
        print(f"{'='*60}\n")
    
    def calculate_euclidean_distance(self, lat1: float, lon1: float, 
                                    lat2: float, lon2: float) -> float:
        """
        Calculate Euclidean distance between two geographic points
        
        Returns:
            Distance in degrees (approximate)
        """
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
    
    def get_rerouting_history(self) -> List[Dict]:
        """Get the history of all rerouting operations"""
        return self.rerouting_history
    
    def get_rerouting_statistics(self) -> Dict:
        """Get statistics about rerouting operations"""
        total_operations = len(self.rerouting_history)
        total_packages = sum(op["packages_rerouted"] for op in self.rerouting_history)
        
        return {
            "total_rerouting_operations": total_operations,
            "total_packages_rerouted": total_packages,
            "average_packages_per_operation": total_packages / total_operations if total_operations > 0 else 0
        }


def calculate_blast_radius(graph: LogisticsGraph, truck_id: str) -> Dict:
    """
    Calculate the blast radius of a truck failure
    Shows how many deliveries will be late and the SLA penalties
    """
    impact = graph.get_impact_analysis(truck_id)
    
    affected_packages = impact["affected_packages"]
    affected_customers = impact["affected_customers"]
    
    # Estimate delays (simplified - in reality would be more complex)
    # Assume 2-4 hours average delay for rerouting
    avg_delay_hours = 3
    
    # Calculate SLA penalties
    penalty_per_package = avg_delay_hours * config.SLA_PENALTY_PER_HOUR
    total_penalty = affected_packages * penalty_per_package
    
    return {
        "affected_deliveries": affected_packages,
        "affected_customers": affected_customers,
        "estimated_delay_hours": avg_delay_hours,
        "sla_penalty_per_package": penalty_per_package,
        "total_sla_penalty": total_penalty,
        "impact_summary": f"This truck failure will cause {affected_packages} late deliveries "
                         f"affecting {affected_customers} customers and cost ${total_penalty:.2f} in SLA penalties."
    }


if __name__ == "__main__":
    # Test the agent
    graph = LogisticsGraph()
    if graph.connect():
        agent = AutonomousReroutingAgent(graph)
        
        print("✓ Rerouting agent initialized")
        print(f"✓ Workflow has {len(agent.workflow.nodes)} nodes")
        
        graph.close()
