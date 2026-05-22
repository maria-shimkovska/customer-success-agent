import logging
logging.disable(logging.INFO)

from agentspan.agents import Agent, AgentRuntime, tool

# ---------------------------------------------------------------------------
# Tools for the agent
# ---------------------------------------------------------------------------
@tool
def get_hubspot_data(customer_id: str) -> dict:
  """Get account details for a customer from HubSpot.
  Returns plan tier, contract value, lifecycle stage, and account owner.
  """

  return {
    "customer_id": customer_id,
    "company": "Sekro",
    "contract_value": 48000,
    "lifecycle_stage": "customer",
    "health_score": 62,
    "account_owner": "jane@yourcompany.com",
  }

@tool
def get_slack_data(customer_id: str) -> dict:
  """Get the 100 most recent Slack messages from the customer's shared channel."""
  return {
    "customer_id": customer_id,
    "channel": "#sekro",
    "messages": [
      {"user": "bob@sekro.com", "text": "Hey, our exports have been failing since Tuesday", "ts": "2025-06-10T09:12:00Z"},
      {"user": "jane@yourcompany.com", "text": "Looking into it now!", "ts": "2025-06-10T09:15:00Z"},
      {"user": "bob@asekro.com", "text": "Still broken — our CFO is asking questions", "ts": "2025-06-11T14:03:00Z"},
      ],
  }

@tool
def open_zendesk_ticket(subject: str, description: str, priority: str = "high") -> dict:
  """Open a support ticket in Zendesk.
  Call this AT MOST ONCE. If the issue needs another ticket, escalate instead.
  """

  return {
    "ticket_id": "ZD-99182",
    "subject": subject,
    "priority": priority,
    "status": "open",
    "url": "https://support.yourcompany.zendesk.com/tickets/99182",
  }

@tool(approval_required=True)
def escalate(reason: str, recommended_action: str) -> dict:
  """Escalate to a human agent.
  Use this when confidence is low, when the issue is high-stakes, or when no available action seems right.
  """
  return {"status": "escalated", "reason": reason, "recommended_action": recommended_action}

# ---------------------------------------------------------------------------
# Agent prompt
# ---------------------------------------------------------------------------
INSTRUCTIONS= """
You are a customer success agent for a SaaS company. 

Your goal is to keep the customer happy. 

You wull be given a customer ID and a description of their issue. Work through the issue step by step:
1. Get the customer's Hubspot data to understand their tier and importance
2. Check their Slack history to understand the full context 
3. Based on what you learn, either open a Zendesk ticket or escalate to a human

Rules: 
- Open a Zendesk ticket AT MOST ONCE. If you already opened one, escalate instead. 
- If you have low confidence at any point, escalate immediately. 
- High-value customers (contracts > $25k) should be escalated if the issue is unresolved after 2 steps. 
"""

# ---------------------------------------------------------------------------
# Define the Agent
# ---------------------------------------------------------------------------
agent = Agent(
  name="CustomerSuccessAgent",
  model="anthropic/claude-sonnet-4-20250514",
  tools=[get_hubspot_data, get_slack_data, open_zendesk_ticket, escalate],
  instructions=INSTRUCTIONS,
  max_turns=5
)

# ---------------------------------------------------------------------------
# Run the Agent
# ---------------------------------------------------------------------------
if __name__ == "__main__":
  print("\n" + "=" * 60)
  print("  CUSTOMER SUCCESS AGENT")
  print("  Investigating: Sekro — export failures (3 days, CFO involved)")
  print("=" * 60 + "\n")

  with AgentRuntime() as runtime:
    handle = runtime.start(agent, "Customer ID: sekro-001. Their data exports have been failing for 3 days and their CFO is getting involved.")
    print(f"Execution ID: {handle.execution_id}\n")

    step = 0
    escalating = False

    def handle_event(event):
      global step, escalating
      if event.type == "tool_call":
        if event.tool_name == "escalate":
          escalating = True
          return  # printed by main thread at approval time
        step += 1
        tool_labels = {
          "get_hubspot_data":    "Looking up customer in HubSpot",
          "get_slack_data":      "Reading Slack channel history",
          "open_zendesk_ticket": "Opening Zendesk support ticket",
        }
        label = tool_labels.get(event.tool_name, event.tool_name)
        print(f"\n  STEP {step}: {label}", flush=True)

      elif event.type == "tool_result":
        if event.tool_name == "get_hubspot_data":
          r = event.result or {}
          print(f"  Company:        {r.get('company', '-')}")
          print(f"  Plan:           {r.get('plan', '-')}")
          print(f"  Contract value: ${r.get('contract_value', '-'):,}")
          print(f"  Health score:   {r.get('health_score', '-')}")
          print(f"  Account owner:  {r.get('account_owner', '-')}", flush=True)

        elif event.tool_name == "get_slack_data":
          r = event.result or {}
          messages = r.get("messages", [])
          print(f"  Channel: {r.get('channel', '-')} — {len(messages)} messages")
          for m in messages:
            print(f"    {m.get('user', '?')}: {m.get('text', '')}")
          print("", flush=True)

        elif event.tool_name == "open_zendesk_ticket":
          r = event.result or {}
          print(f"  Ticket ID: {r.get('ticket_id', '-')}")
          print(f"  Priority:  {r.get('priority', '-')}")
          print(f"  URL:       {r.get('url', '-')}", flush=True)

      elif event.type == "done":
        output = event.output
        result_text = output.get("result", output) if isinstance(output, dict) else output
        print("\n" + "=" * 60)
        print("  AGENT SUMMARY")
        print("=" * 60)
        print(f"\n{result_text}\n", flush=True)

    import threading
    import time
    import os
    import tty as tty_lib
    import termios

    def read_char():
      """Read a single keypress directly from the terminal."""
      fd = os.open("/dev/tty", os.O_RDWR)
      old = termios.tcgetattr(fd)
      try:
        tty_lib.setraw(fd)
        termios.tcflush(fd, termios.TCIFLUSH)
        ch = os.read(fd, 1).decode("utf-8", errors="replace")
      finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        os.close(fd)
      return ch

    pause_printing = threading.Event()
    stream_done = threading.Event()

    def run_stream():
      for event in handle.stream():
        if not pause_printing.is_set():
          handle_event(event)
      stream_done.set()

    t = threading.Thread(target=run_stream, daemon=True)
    t.start()

    # Poll for human approval while stream runs in background
    while not stream_done.is_set():
      time.sleep(2)
      status = handle.get_status()
      if status.is_waiting:
        pause_printing.set()
        time.sleep(0.2)  # let stream thread finish its current print
        pt = status.pending_tool or {}
        args = pt.get("args") or pt  # args may be nested or flat
        if escalating:
          step += 1
          print(f"\n  STEP {step}: Preparing to escalate to human")
        print("\n" + "=" * 60)
        print("  HUMAN APPROVAL REQUIRED")
        print("=" * 60)
        print(f"\n  The agent has reviewed the customer data and is requesting")
        print(f"  permission to escalate this issue to a human agent.")
        print("\n  Approve? (y/n): ", end="", flush=True)
        answer = read_char().lower()
        print(answer)
        if answer == "y":
          handle.approve()
          print("\n  Approved — resuming agent...\n")
          pause_printing.clear()
        else:
          handle.reject("Escalation not approved")
          print("\n  Escalation rejected.\n")
          result = handle.join()
          output = result.output or {}
          result_text = output.get("result", output) if isinstance(output, dict) else output
          print("\n" + "=" * 60)
          print("  AGENT SUMMARY")
          print("=" * 60)
          if result_text:
            print(f"\n{result_text}\n")
          else:
            print("\n  Escalation was rejected. No further action was taken.\n")
        break

    t.join(timeout=120)
