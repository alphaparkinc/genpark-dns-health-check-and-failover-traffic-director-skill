"""Example usage for DNS Health Check and Failover Traffic Director."""
from client import DNSHealthTrafficDirector


def main():
    director = DNSHealthTrafficDirector(consecutive_failure_threshold=3, consecutive_success_threshold=2)
    primary = "us-east-1.app.enterprise.com"
    standby = "us-west-2.app.enterprise.com"

    print("=== 1. Probing Initial Healthy State ===")
    director.record_probe(primary, is_healthy=True, latency_ms=45.0)
    director.record_probe(standby, is_healthy=True, latency_ms=85.0)

    decision1 = director.resolve_traffic_routing(primary, standby)
    print("Decision:", decision1["routing_decision"])
    print("Routed Endpoint:", decision1["routed_endpoint"])
    print("Failover Active:", decision1["failover_active"])

    print("\n=== 2. Primary Endpoint Outage (Simulating 3 Consecutive Probe Failures) ===")
    for i in range(3):
        res = director.record_probe(primary, is_healthy=False, latency_ms=5000.0)
        print(f"Probe #{i+1} -> Status: {res['status']} (Consecutive Failures: {res['consecutive_failures']})")

    decision2 = director.resolve_traffic_routing(primary, standby)
    print("\nPost-Outage Decision:", decision2["routing_decision"])
    print("Routed Endpoint:", decision2["routed_endpoint"])
    print("Failover Active:", decision2["failover_active"])
    print("Message:", decision2["message"])

    print("\n=== 3. Primary Endpoint Recovery (Simulating Consecutive Success Probes) ===")
    director.record_probe(primary, is_healthy=True, latency_ms=42.0)
    director.record_probe(primary, is_healthy=True, latency_ms=40.0)

    decision3 = director.resolve_traffic_routing(primary, standby)
    print("Post-Recovery Decision:", decision3["routing_decision"])
    print("Routed Endpoint:", decision3["routed_endpoint"])
    print("Failover Active:", decision3["failover_active"])


if __name__ == "__main__":
    main()
