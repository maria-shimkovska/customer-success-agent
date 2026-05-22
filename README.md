# Customer Success Agent

An AI-powered customer success agent built with [AgentSpan](https://agentspan.dev). Given a customer ID and issue description, the agent automatically investigates by pulling CRM and Slack data, then either opens a support ticket or escalates to a human — with a built-in human-in-the-loop approval step for escalations.

## What it does

1. Fetches the customer's account details from HubSpot (tier, contract value, health score)
2. Reads recent Slack channel history to understand the full context
3. Decides to either open a Zendesk ticket or escalate to a human agent
4. Requires human approval before escalating (interactive prompt in the terminal)

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)
- The `agentspan` package

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/maria-shimkovska/customer-success-agent.git
   cd customer-success-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install agentspan
   ```

4. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Running the agent

```bash
python agent.py
```

The agent will print each step as it works through the issue. If it decides to escalate, it will pause and prompt you for approval:

```
  HUMAN APPROVAL REQUIRED
  The agent has reviewed the customer data and is requesting
  permission to escalate this issue to a human agent.

  Approve? (y/n):
```

- Press `y` to approve the escalation and let the agent continue
- Press `n` to reject it — the agent will wrap up without escalating

## Customizing

The demo uses hardcoded mock data in the tool functions (`get_hubspot_data`, `get_slack_data`, `open_zendesk_ticket`). To connect real services, replace the return values in each tool with actual API calls to HubSpot, Slack, and Zendesk.

To change the customer scenario, update the prompt in the `runtime.start(...)` call at the bottom of `agent.py`.
