"""DNS Health Check and Failover Traffic Director.
100% Python Standard Library.
"""

import time
from typing import Dict, Any, List, Optional
from collections import deque


class DNSHealthTrafficDirector:
    """Evaluates multi-region endpoint health checks, calculates rolling latency and
    consecutive failure triggers, and directs DNS traffic to healthy standby targets upon failover."""

    def __init__(
        self,
        consecutive_failure_threshold: int = 3,
        consecutive_success_threshold: int = 2,
        history_window_size: int = 10,
    ):
        self.consecutive_failure_threshold = consecutive_failure_threshold
        self.consecutive_success_threshold = consecutive_success_threshold
        self.history_window_size = history_window_size

        # Maps endpoint_id -> dict of state
        self.endpoints: Dict[str, Dict[str, Any]] = {}

    def record_probe(
        self,
        endpoint_id: str,
        is_healthy: bool,
        latency_ms: float,
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Records a synthetic or passive health probe result."""
        now = timestamp if timestamp is not None else time.time()

        if endpoint_id not in self.endpoints:
            self.endpoints[endpoint_id] = {
                "endpoint_id": endpoint_id,
                "status": "HEALTHY",
                "consecutive_failures": 0,
                "consecutive_successes": 0,
                "probes": deque(maxlen=self.history_window_size),
                "last_state_change": now,
            }

        ep = self.endpoints[endpoint_id]
        ep["probes"].append({"healthy": is_healthy, "latency_ms": latency_ms, "time": now})

        prior_status = ep["status"]

        if is_healthy:
            ep["consecutive_successes"] += 1
            ep["consecutive_failures"] = 0
            if prior_status != "HEALTHY" and ep["consecutive_successes"] >= self.consecutive_success_threshold:
                ep["status"] = "HEALTHY"
                ep["last_state_change"] = now
        else:
            ep["consecutive_failures"] += 1
            ep["consecutive_successes"] = 0
            if prior_status != "UNHEALTHY" and ep["consecutive_failures"] >= self.consecutive_failure_threshold:
                ep["status"] = "UNHEALTHY"
                ep["last_state_change"] = now

        # Compute average latency
        avg_latency = round(sum(p["latency_ms"] for p in ep["probes"]) / len(ep["probes"]), 2)

        return {
            "endpoint_id": endpoint_id,
            "probe_healthy": is_healthy,
            "latency_ms": latency_ms,
            "avg_latency_ms": avg_latency,
            "status": ep["status"],
            "state_changed": prior_status != ep["status"],
            "consecutive_failures": ep["consecutive_failures"],
            "consecutive_successes": ep["consecutive_successes"],
        }

    def resolve_traffic_routing(
        self,
        primary_endpoint: str,
        standby_endpoint: str,
    ) -> Dict[str, Any]:
        """Resolves active DNS routing target based on primary and standby health status."""
        p_status = self.endpoints.get(primary_endpoint, {}).get("status", "HEALTHY")
        s_status = self.endpoints.get(standby_endpoint, {}).get("status", "HEALTHY")

        if p_status == "HEALTHY":
            return {
                "routing_decision": "PRIMARY_ACTIVE",
                "routed_endpoint": primary_endpoint,
                "failover_active": False,
                "primary_status": p_status,
                "standby_status": s_status,
                "message": f"Primary endpoint '{primary_endpoint}' is healthy.",
            }
        elif s_status == "HEALTHY":
            return {
                "routing_decision": "FAILOVER_STANDBY_ACTIVE",
                "routed_endpoint": standby_endpoint,
                "failover_active": True,
                "primary_status": p_status,
                "standby_status": s_status,
                "message": f"Failover activated! Primary '{primary_endpoint}' is {p_status}; traffic diverted to standby '{standby_endpoint}'.",
            }
        else:
            # Both degraded -> fallback to primary with emergency alert
            return {
                "routing_decision": "ALL_ENDPOINTS_DEGRADED",
                "routed_endpoint": primary_endpoint,
                "failover_active": False,
                "primary_status": p_status,
                "standby_status": s_status,
                "message": "CRITICAL: Both primary and standby endpoints are unhealthy! Serving primary as best-effort.",
            }
