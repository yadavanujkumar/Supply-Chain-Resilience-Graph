import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Google Maps API
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Simulation Parameters
SIMULATION_INTERVAL = 5  # seconds between disruption checks
SLA_PENALTY_PER_HOUR = 10  # dollars per hour of delay
TRUCK_SPEED_KMH = 60  # average truck speed in km/h
