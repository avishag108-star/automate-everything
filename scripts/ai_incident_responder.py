"""
AI Incident Responder — powered by Claude
-----------------------------------------
When a pod crashes or an alert fires, this script:
  1. Reads the pod logs
  2. Sends them to Claude
  3. Gets a plain-Hebrew explanation + fix steps
  4. Sends to Slack/email

Run manually: python scripts/ai_incident_responder.py --pod statuswatch-xxx-yyy
Or trigger from Grafana alert webhook.
"""

import anthropic
import subprocess
import argparse
import os


def get_pod_logs(pod_name: str, namespace: str = "statuswatch", lines: int = 100) -> str:
    """Get the last N log lines from a crashing pod."""
    result = subprocess.run(
        ["kubectl", "logs", pod_name, "-n", namespace,
         f"--tail={lines}", "--previous"],
        capture_output=True, text=True
    )
    return result.stdout or result.stderr


def get_pod_events(pod_name: str, namespace: str = "statuswatch") -> str:
    """Get Kubernetes events for a pod."""
    result = subprocess.run(
        ["kubectl", "describe", "pod", pod_name, "-n", namespace],
        capture_output=True, text=True
    )
    return result.stdout[:3000]


def analyze_incident(logs: str, events: str, pod_name: str) -> str:
    """Send logs to Claude and get incident analysis."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""You are a DevOps on-call engineer. A Kubernetes pod has crashed.
Analyze the logs and events, then explain in simple terms (as if explaining to a junior engineer):

1. What happened (root cause)
2. How urgent is this (P1/P2/P3)
3. Exact steps to fix it right now
4. How to prevent it in the future

Pod: {pod_name}

--- LOGS ---
{logs}

--- K8S EVENTS ---
{events}

Be direct and actionable. No fluff."""
        }]
    )

    return message.content[0].text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pod", required=True, help="Pod name to analyze")
    parser.add_argument("--namespace", default="statuswatch")
    args = parser.parse_args()

    print(f"🔍 Collecting data for pod: {args.pod}")
    logs = get_pod_logs(args.pod, args.namespace)
    events = get_pod_events(args.pod, args.namespace)

    print("🤖 Analyzing with Claude...")
    analysis = analyze_incident(logs, events, args.pod)

    print("\n" + "="*60)
    print("🚨 INCIDENT ANALYSIS")
    print("="*60)
    print(analysis)
    print("="*60)


if __name__ == "__main__":
    main()
