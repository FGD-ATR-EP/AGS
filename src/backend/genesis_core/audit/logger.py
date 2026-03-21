import logging
import os
import json
from datetime import datetime

class EvolutionLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.evolution_log_path = os.path.join(self.log_dir, "evolution.log")
        self.genesis_cycle_log_path = os.path.join(self.log_dir, "genesis_cycle.log")

        # Setup logging configurations
        self.evolution_logger = self._setup_logger("evolution_logger", self.evolution_log_path)
        self.genesis_cycle_logger = self._setup_logger("genesis_cycle_logger", self.genesis_cycle_log_path)

    def _setup_logger(self, name, log_file):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        # Avoid duplicate handlers if the logger is already setup
        if not logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def log_evolution_event(self, event_type, details):
        """Logs an evolution event to evolution.log."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.evolution_logger.info(json.dumps(log_entry))

    def log_genesis_cycle(self, cycle_id, phase, outcome):
        """Logs a genesis cycle event to genesis_cycle.log."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle_id": cycle_id,
            "phase": phase,
            "outcome": outcome
        }
        self.genesis_cycle_logger.info(json.dumps(log_entry))

    def read_logs(self, log_type="evolution", limit=100):
        """Reads the last N logs of the specified type."""
        log_path = self.evolution_log_path if log_type == "evolution" else self.genesis_cycle_log_path
        if not os.path.exists(log_path):
            return []

        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()
                # Parse the JSON part of the log line (skipping the timestamp/level prefix if any,
                # but our formatter puts everything after the prefix. Actually, let's just parse the line content after the " - " separator if possible,
                # or just parse the whole line if the format is strictly JSON.
                # Wait, my formatter is '%(asctime)s - %(levelname)s - %(message)s'.
                # So the JSON is in the message part.
                parsed_logs = []
                for line in lines[-limit:]:
                    try:
                        # Split by " - " and take the last part (message)
                        parts = line.split(" - ", 2)
                        if len(parts) >= 3:
                            message = parts[2]
                            parsed_logs.append(json.loads(message))
                    except json.JSONDecodeError:
                        continue
                return parsed_logs
        except Exception as e:
            print(f"Error reading logs: {e}")
            return []
