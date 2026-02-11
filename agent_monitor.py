import time

class NetworkMonitor:
    def __init__(self):
        self.trust_score = 100.0
        self.uptime_seconds = 0
        self.tasks_completed = 0

    def calculate_reputation(self):
        """
        Logic for dynamic reputation scoring (0-1000).
        Ref: Reputation Score & Consensus Mechanism v1.1
        """
        # Basic formula: Base 500 + (tasks * 2) - (downtime penalty)
        score = 500 + (self.tasks_completed * 2)
        return min(max(score, 0), 1000)

    def log_event(self, event_type, details):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"🔍 [MONITOR] {timestamp} | {event_type} | {details}")

    def run(self):
        self.log_event("STARTUP", "ProxyAgent Network Monitor Active")
        try:
            while True:
                # Simulate monitoring loop
                reputation = self.calculate_reputation()
                self.log_event("HEALTH", f"Current Reputation: {reputation} | Uptime: {self.uptime_seconds}s")
                
                self.uptime_seconds += 10
                time.sleep(10)
        except KeyboardInterrupt:
            self.log_event("SHUTDOWN", "Monitor suspended by operator")

if __name__ == "__main__":
    monitor = NetworkMonitor()
    monitor.run()