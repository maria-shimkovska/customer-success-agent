# Customer Success Agent

An AI agent that investigates customer issues end-to-end — pulling live CRM and Slack data, deciding on the right action, and handing off to a human when it matters. Built with [Agentspan](https://agentspan.ai).

<video src="customer_success_agent.mp4" controls width="100%"></video>

---

## How it works

Drop in a customer ID and a problem description. The agent takes it from there:

1. **Looks up the customer in HubSpot** — contract value, health score, lifecycle stage, account owner
2. **Reads their Slack channel** — understands the full conversation history and urgency
3. **Takes action** — opens a Zendesk ticket or escalates to a human, based on what it finds
4. **Asks before escalating** — if it wants to loop in a human, it pauses and asks you first

High-value customers (contracts over $25k) get prioritized automatically. Low-confidence situations trigger an escalation rather than a guess.

---

## Demo

The agent works through a real scenario: a customer whose exports have been failing for 3 days with their CFO getting involved. Watch the video above to see it run live.

---

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)
- The `agentspan` package

---

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

---

## Run it

```bash
python agent.py
```

You'll see each step printed as the agent works through the issue:

```
============================================================
  CUSTOMER SUCCESS AGENT
  Investigating: Sekro — export failures (3 days, CFO involved)
============================================================

  STEP 1: Looking up customer in HubSpot
  Company:        Sekro
  Contract value: $48,000
  Health score:   62

  STEP 2: Reading Slack channel history
  Channel: #sekro — 3 messages
    bob@sekro.com: Hey, our exports have been failing since Tuesday
    ...

  STEP 3: Preparing to escalate to human

============================================================
  HUMAN APPROVAL REQUIRED
============================================================

  The agent has reviewed the customer data and is requesting
  permission to escalate this issue to a human agent.

  Approve? (y/n):
```

Press `y` to approve the escalation or `n` to reject it. That's it.

---

## Customize it

The tool functions (`get_hubspot_data`, `get_slack_data`, `open_zendesk_ticket`) return hardcoded mock data by default. To wire up real services, replace the `return` values with actual API calls.

To change the scenario, update the prompt passed to `runtime.start(...)` at the bottom of `agent.py`.
