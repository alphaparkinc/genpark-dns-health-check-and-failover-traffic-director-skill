"""MCP server for DNS Health Check and Failover Traffic Director."""
import sys
import json
from client import DNSHealthTrafficDirector

_director = DNSHealthTrafficDirector()


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "record_probe",
                    "description": "Records an endpoint health probe and evaluates consecutive failure thresholds",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "endpoint_id": {"type": "string"},
                            "is_healthy": {"type": "boolean"},
                            "latency_ms": {"type": "number"},
                        },
                        "required": ["endpoint_id", "is_healthy", "latency_ms"],
                    },
                },
                {
                    "name": "resolve_traffic_routing",
                    "description": "Resolves whether primary or standby endpoint should receive DNS traffic based on health states",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "primary_endpoint": {"type": "string"},
                            "standby_endpoint": {"type": "string"},
                        },
                        "required": ["primary_endpoint", "standby_endpoint"],
                    },
                },
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "record_probe":
            res = _director.record_probe(
                endpoint_id=args.get("endpoint_id"),
                is_healthy=args.get("is_healthy"),
                latency_ms=float(args.get("latency_ms", 0.0)),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "resolve_traffic_routing":
            res = _director.resolve_traffic_routing(
                primary_endpoint=args.get("primary_endpoint"),
                standby_endpoint=args.get("standby_endpoint"),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()
