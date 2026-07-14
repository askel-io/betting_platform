import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from config.settings import get_settings

_settings = get_settings()

DATABASE_URL = _settings.line_provider_database_url
KAFKA_ENABLED = _settings.kafka_enabled
KAFKA_BOOTSTRAP_SERVERS = _settings.kafka_bootstrap_servers
KAFKA_EVENT_FINISHED_TOPIC = _settings.kafka_event_finished_topic

settings = _settings
