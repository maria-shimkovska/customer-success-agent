# Customer Success Agent

An AI agent that investigates customer issues end-to-end — pulling live CRM and Slack data, deciding on the right action, and looping in a human when it matters. Built with [Agentspan](https://agentspan.ai).

<video src="https://github.com/user-attachments/assets/9796d98d-05e0-422e-8bb1-2ab12a390140" controls width="100%"></video>

---

## Why try this

This project is a good example of what an AI agent actually looks like in practice. It is simple enough to understand quickly, but it demonstrates the core mechanics that make agents useful: the model reasons about a situation, calls real tools to fetch data, and makes decisions based on what it finds.

When you run it, you can watch that process happen in the terminal. You see the data it pulls, the steps it takes, and if it decides the situation needs a human, it pauses and asks you directly. That human-in-the-loop checkpoint is one of the more interesting parts to see in action.

It is not a polished product or a production-ready feature, it is a demo, but it shows the idea well. It shows how fast you can go from an idea to something that actually works, and the use case itself, helping a customer success team triage and respond to at-risk accounts, is the kind of real business problem that AI agents are genuinely well suited to solve.

---

## What it does

Give it a customer ID and a description of the problem. It works through the issue step by step:

1. **Looks up the customer in HubSpot** — contract value, health score, lifecycle stage, account owner
2. **Reads their Slack channel** — understands the full conversation history and urgency
3. **Takes action** — either opens a Zendesk ticket or requests human intervention, based on what it found

High-value customers (contracts over $25k) get escalated automatically if the issue isn't resolved quickly. Low-confidence situations escalate rather than guess.

---

## What to expect when you run it

The agent prints each step as it goes. Most of the time it runs fully on its own and ends with a summary.

If it decides the situation needs a human, it **pauses and asks you** before doing anything:

```
============================================================
  HUMAN APPROVAL REQUIRED
============================================================

  [Situation summary — who the customer is, what's wrong,
   what the agent already did, and why it's escalating]

  Mark as resolved? (y/n):
```

**Press `y`** — marks it as resolved. The agent continues running and prints a final summary when done.

**Press `n`** — rejects the intervention. The agent wraps up and prints a summary of what happened.

Either way, you always get a final summary at the end.

---

## Demo

The agent works through a real scenario: a customer whose exports have been failing for 3 days with their CFO now involved. Watch the video above to see it run live.

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
   pip install agentspan anthropic
   ```
   - `agentspan` — runs the agent, manages tool calls, and handles the human approval flow
   - `anthropic` — used directly to call Claude for summarizing data and generating situation briefs

4. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

---

## Run it

```bash
python agent.py
```

You can also pass the issue directly as an argument:

```bash
python agent.py "Sekro — export failures, 3 days, CFO involved"
```

---

## Other inputs to try

The mock data always returns the same Sekro account ($48k contract, health score 62, CFO involved). What changes is how the agent reasons about the situation based on your description.

**Trigger an automatic Zendesk ticket** — describe a straightforward, low-urgency issue:
```bash
python agent.py "Sekro — user can't find the export button, first time asking"
```

**Trigger immediate human escalation** — mention high stakes or executive involvement:
```bash
python agent.py "Sekro — full data loss reported, legal team is involved"
```

**Test low-confidence handling** — give a vague or ambiguous description:
```bash
python agent.py "Sekro — something seems off with their account, not sure what"
```

**Simulate a billing dispute** — a different issue type to see how the agent adapts:
```bash
python agent.py "Sekro — disputing their last invoice, threatening to cancel"
```

**Try without a customer name** — see how the agent handles missing context:
```bash
python agent.py "exports broken for 3 days, CFO is angry"
```

---

## Customize it

The tool functions (`get_hubspot_data`, `get_slack_data`, `open_zendesk_ticket`) return hardcoded mock data by default. To wire up real services, replace the `return` values with actual API calls.

To change the scenario, update the prompt passed to `runtime.start(...)` at the bottom of `agent.py`.
