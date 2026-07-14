import os

KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "true").lower() == "true"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_EVENT_FINISHED_TOPIC = os.getenv("KAFKA_EVENT_FINISHED_TOPIC", "event.finished")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "bet-maker")
LINE_PROVIDER_URL = os.getenv("LINE_PROVIDER_URL", "http://localhost:8001")
