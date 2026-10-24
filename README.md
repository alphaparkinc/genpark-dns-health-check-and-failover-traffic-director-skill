# genpark-dns-health-check-and-failover-traffic-director-skill

Multi-region DNS health probe evaluator, automated failover traffic director, and latency-based routing arbiter.

100% Python Standard Library implementation with zero external dependencies.

## Key Capabilities

- **Synthetic Health Check Evaluation**: Tracks latency jitter, probe successes, and consecutive failure counts.
- **Flap Damping & State Transition Stabilization**: Enforces separate failure and success hysteresis thresholds to eliminate rapid route flipping during intermittent network instability.
- **Automated Active-Standby Failover**: Automatically steers DNS queries away from unhealthy regions to secondary warm standbys.
- **Zero-Dependency Rolling Window Statistics**: Maintains recent probe telemetry using fixed-size collections without external databases.

## Architecture

```
[Periodic Health Probes: HTTP Status, Latency, Endpoint ID]
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               DNSHealthTrafficDirector                 │
│  - Hysteresis Consecutive Failure / Success Arbiter    │
│  - Rolling Latency Jitter & Health State Tracker       │
│  - Failover Traffic Steering Finite State Machine      │
│  - Active DNS Record Target Resolver                   │
└────────────────────────────────────────────────────────┘
          │                                  │
  (Primary Healthy)                  (Primary Unhealthy)
          ▼                                  ▼
[Route to Primary Region]          [Auto-Failover to Standby Region]
```

## MCP Server Integration

Run standard MCP stdio server:
```bash
python mcp_server.py
```

Exposed Tools:
- `record_probe`: Records an endpoint health probe and evaluates consecutive failure thresholds.
- `resolve_traffic_routing`: Resolves whether primary or standby endpoint should receive DNS traffic based on health states.

## Quickstart (Python API)

```python
from client import DNSHealthTrafficDirector

director = DNSHealthTrafficDirector()
director.record_probe("us-east", is_healthy=True, latency_ms=30.0)
route = director.resolve_traffic_routing("us-east", "us-west")
print("Target:", route["routed_endpoint"])
```

---

## GenPark Ecosystem

- **Official Website**: [https://www.genpark.ai](https://www.genpark.ai)
- **LinkedIn Page**: [https://www.linkedin.com/company/92955550](https://www.linkedin.com/company/92955550)
