
# Plan for presentation: Adding a human in the loop to agentic workflows

This is the plan for the presentation on adding a human in the loop to agentic workflows using the Microsoft Agent Framework. The presentation will cover how to incorporate human interactions into agentic workflows, including requests and responses, tool approval, checkpoints and resuming, handoff with HITL, and Magentic with HITL. The presentation will include live examples and demos to illustrate these concepts in action.

In this plan, we will figure out the exact slides and code samples.

## Slide references:

See the previous two talks about agentic workflows. ASCII exports here:

* [First workflows](first_workflows.md)
* [Advanced workflows](advanced_workflows.md)

## Description:
In the final session of our Python + Agents series, we’ll explore how to incorporate human‑in‑the‑loop (HITL) interactions into 
agentic workflows using the Microsoft Agent Framework. This session focuses on adding points where a workflow can pause, 
request input or approval from a user, and then resume once the human has responded. HITL is especially important because 
LLMs can produce uncertain or inconsistent outputs, and human checkpoints provide an added layer of accuracy and oversight.
We’ll begin with the framework’s requests‑and‑responses model, which provides a structured way for workflows to ask questions, 
collect human input, and continue execution with that data. We'll move onto tool approval, one of the most frequent reasons an 
agent requests input from a human, and see how workflows can surface pending tool calls for approval or rejection.
Next, we’ll cover checkpoints and resuming, which allow workflows to pause and be restarted later. This is especially important 
for HITL scenarios where the human may not be available immediately. We’ll walk through examples that demonstrate how 
checkpoints store progress, how resuming picks up the workflow state, and how this mechanism supports longer‑running or 
multi‑step review cycles.
This session brings together everything from the series—agents, workflows, branching, orchestration—and shows how to 
integrate humans thoughtfully into AI‑driven processes, especially when reliability and judgment matter most.
Prerequisites: To follow along with the live examples, sign up for a free GitHub account. If you are brand new to generative AI 
with Python, start with our 9-part Python + AI series, which covers LLMs, embedding models, RAG, tool calling, MCP, and more.

## Outline:

• Requests and responses
    • All samples: https://github.com/microsoft/agentframework/tree/main/python/samples/getting_started/workflows#human-in-the-loop
    • https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/requests-and-responses?pivots=programming-language-python
    • https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/workflows/humanin-the-loop/guessing_game_with_human_input.py
    • https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/requests-and-responses?pivots=programming-language-python

• Tool approval (generally, one of the most common reasons for user input)
    All samples: https://github.com/microsoft/agentframework/tree/main/python/samples/getting_started/workflows#tool-approval

• Checkpoints & resuming
    • Necessary for long-running tasks, but also relevant to HITL since a workflow may be paused if the human is not 
    currently available.
    • All samples: https://github.com/microsoft/agentframework/tree/main/python/samples/getting_started/workflows#checkpoint
    • https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/checkpointing-and-resuming?pivots=programming-language-python
    • https://github.com/microsoft/agentframework/blob/main/python/samples/getting_started/workflows/checkpoint/checkpoint_with_resume.py
    • https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/checkpoints?pivots=programminglanguage-python

• Handoff with HITL
    • User input requests: https://learn.microsoft.com/en-us/agent-framework/userguide/workflows/orchestrations/handoff?pivots=programming-language-python#run-interactive-handoff-workflow1
    • Tool approval: https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/handoff?
    pivots=programming-language-python#advanced-tool-approval-in-handoff-workflows

• Magentic with HITL
    • Plan review and tool approval: https://learn.microsoft.com/en-us/agent-framework/userguide/workflows/orchestrations/magentic?pivots=programming-language-python#advanced-human-in-the-loopplan-review

---

## Open Questions

- Discuss durability, agent inbox?
- Do we need a diagram explaining the Coordinator + Agent pattern for HITL?
  - The HITL examples use a custom Executor (ChatCoordinator/TripCoordinator) that sits between
    the application and the Agent node. The Coordinator handles request_info/response_handler,
    while the Agent does the LLM work. This two-node pattern might not be obvious — people may
    wonder why we can't just call request_info directly from the Agent.
  - A simple workflow diagram (Coordinator ↔ Agent with labels showing which node does what)
    could help, especially before the code slides. Something like:
    ```
    Input → [Coordinator] ↔ [Agent]
              │                │
              │ request_info   │ LLM call
              │ response_handler│
              ▼
            Output
    ```
  - On the other hand, this is really just the standard Executor→Agent edge pattern from
    Session 1 (workflow_agents.py). Adding a diagram might over-explain something familiar.
  - Recommendation: probably worth a quick visual on the slide before the code, showing the
    two-node loop. Keep it simple — one box labeled "Coordinator (Executor)" and one labeled
    "Agent", with bidirectional edges and a callout showing where request_info happens.

## TODOs

- Add Davide's banking assistant as E2E app example at end of slides
  - https://github.com/Azure-Samples/agent-openai-python-banking-assistant/blob/main/app/backend/app/ag... (AzureOpenAIChatClient)
  - https://github.com/Azure-Samples/agent-openai-python-banking-assistant/tree/main/app/backend/app/ag... (Foundry Agent Service v2)
  - Interesting patterns not in MAF samples:
    - How to manage checkpoint storage per user/thread id
    - Resume workflow on multi-turn conversations
    - Resume workflow on tool approval response

## Finalized Plan

### Code Samples to Create (5 files + 5 Spanish translations)

| # | File | Concept | Key APIs |
|---|------|---------|----------|
| 1 | `examples/workflow_hitl_requests_structured.py` | Trip planner — user gives a vague request, agent asks clarifying questions (destination, budget, interests, dates), human answers each, agent produces itinerary | `ctx.request_info()`, `@response_handler`, `WorkflowEvent(type="request_info")` |
| 2 | `examples/workflow_hitl_tool_approval.py` | Email agent with tools requiring approval before execution | `@tool(approval_mode="always_require")`, `FunctionApprovalRequestContent`, `to_function_approval_response()` |
| 3 | `examples/workflow_hitl_checkpoint.py` | Content review with pause/resume across process restarts | `FileCheckpointStorage`, `on_checkpoint_save/restore`, `workflow.run(checkpoint_id=...)` |
| 4 | `examples/workflow_hitl_handoff.py` | Customer support with triage/refund/order agents + user input + tool approval | `HandoffBuilder`, `HandoffAgentUserRequest`, combined user-input + tool-approval loop |
| 5 | `examples/workflow_hitl_magentic.py` | Research task with Magentic plan review before execution | `MagenticBuilder(enable_plan_review=True)`, `MagenticPlanReviewRequest`, `approve()`/`revise()` |

Each has a corresponding `examples/spanish/workflow_hitl_*.py` translation per AGENTS.md conventions.

**MAF reference samples to adapt** (replace `AzureOpenAIResponsesClient` with `OpenAIChatClient` + `API_HOST`):
- `python/samples/03-workflows/human-in-the-loop/guessing_game_with_human_input.py`
- `python/samples/03-workflows/human-in-the-loop/agents_with_approval_requests.py`
- `python/samples/03-workflows/checkpoint/checkpoint_with_human_in_the_loop.py`
- `python/samples/03-workflows/orchestrations/handoff_with_tool_approval_checkpoint_resume.py`

### Implementation Steps

**Phase 1: Code Samples** (all 5 can be parallelized)
1. Create `examples/workflow_hitl_requests_structured.py` — trip planner with `ctx.request_info()` / `@response_handler`
2. Create `examples/workflow_hitl_tool_approval.py` — email agent with `@tool(approval_mode="always_require")`
3. Create `examples/workflow_hitl_checkpoint.py` — checkpoint + HITL resume with `FileCheckpointStorage`
4. Create `examples/workflow_hitl_handoff.py` — handoff with user input + tool approval
5. Create `examples/workflow_hitl_magentic.py` — Magentic plan review with `enable_plan_review=True`

**Phase 2: Spanish Translations** (*depends on Phase 1*)
6. Create all 5 `examples/spanish/workflow_hitl_*.py` translations

**Phase 3: Slides** (*parallel with Phase 1-2*)
7. Create `presentations/english/session-3/README.md` with ~29 ASCII slides

### Decisions
- **Client pattern**: Use existing `OpenAIChatClient` + `API_HOST` (github/azure/openai) pattern
- **Scenarios**: Trip planner (requests), email agent (tool approval), content review (checkpoints), customer support (handoff), research (Magentic)
- **Magentic**: Full runnable example
- **Spanish**: All 5 files get translations per AGENTS.md rules

### Verification
1. Each `.py` parses without errors: `python -c "import ast; ast.parse(open('file.py').read())"`
2. Ruff lint passes: `uv run ruff check examples/workflow_hitl_*.py examples/spanish/workflow_hitl_*.py`
3. Spanish translations have identical function/class names but Spanish comments/docstrings/prompts
4. All imports reference `agent_framework`
5. Python >=3.10 compatible (`typing_extensions.Never`, not `typing.Never`)

## Slides

### Slide 1: Series overview
```
Python + Agents
Feb 24: Building your first agent in Python
Feb 25: Adding context and memory to agents
Feb 26: Monitoring and evaluating agents
Mar 3: Building your first AI-driven workflows
Mar 4: Orchestrating advanced multi-agent workflows
Mar 5: Adding a human-in-the-loop to workflows ← Today

Register at aka.ms/PythonAgents/series
```

### Slide 2: Title slide
```
Python + Agents
     Adding a human-in-the-loop to workflows
aka.ms/pythonagents/slides/hitlworkflows
Pamela Fox
Python Cloud Advocate
www.pamelafox.org
```

### Slide 3: Today we'll cover...
```
Today we'll cover...
• Why HITL matters for agentic workflows
• Tool approval: gating sensitive operations
• Requests and responses: structured human interaction
• Checkpoints and resuming: durable HITL workflows
• Handoff with HITL: interactive multi-agent routing
```

### Slide 4: Follow along
```
Want to follow along?
1. Open this GitHub repository:
aka.ms/python-agentframework-demos

2. Use "Code" button to create a GitHub Codespace:




3. Wait a few minutes for Codespace to start up
```

### Slide 5: Recap - What's an agentic workflow?
```
Recap: What's an agentic workflow?
An agentic workflow is a flow that involves an agent at some point,
typically to handle decision making or answer synthesis.
                                          Agent
               Processing                                 Processing
 Input              or                    LLM                  or         Output
               Data Lookup                                Data Lookup
                                   Tool         Tool

In agent-framework, a workflow is a graph with Executor nodes and edges between:

               Executor     edge    Executor           edge   Executor
   Input                                                                 Output
```

### Slide 6: Section — Why HITL?
```
Why add a human in the loop?
```

### Slide 7: Why HITL matters
```
Why add a human in the loop?

LLMs can produce uncertain, inconsistent, or incorrect outputs.

Human checkpoints provide:

• Accuracy     — Verify factual correctness before acting
• Safety       — Gate sensitive operations (refunds, emails, deployments)
• Trust        — Users see what the system will do before it acts
• Compliance   — Audit trail of human approvals for regulated workflows
• Control      — Humans can redirect, refine, or halt a workflow at any point
```

### Slide 8: HITL patterns overview
```
HITL patterns in agent-framework

                 Pattern                   When to use

                 Tool Approval             Sensitive tool calls must be approved
                                           before execution (refunds, emails, etc.)
                                           Works with standalone Agent or workflows.

                 Requests & Responses      Workflow needs human input to continue
                                           (answers, choices, feedback)

                 Checkpoints & Resuming    Long-running tasks where human may not
                                           be immediately available

                 Handoff + HITL            Multi-agent routing with interactive
                                           user input between handoffs

                 Magentic + HITL           Complex planning with human review
                                           before executing multi-step plans
                                           (not covered today)
```

### Slide 9: Section — Tool Approval
```
Tool Approval
https://learn.microsoft.com/agent-framework/agents/tools/tool-approval
```

### Slide 10: Why tool approval?
```
Why require tool approval?

 Without approval:                     With approval:

 Agent decides to send email  ──►      Agent wants to send email  ──►
 Tool executes automatically           Agent pauses
 Email sent (possibly wrong!)          Human reviews: "Send to alice@contoso?"
                                       Human approves ✓  or rejects ✗
                                       Tool executes only if approved

Use approval for:
• Financial operations (refunds, purchases)
• Communications (emails, messages)
• Destructive operations (deletions, deployments)
• Any irreversible action

💡 Tool approval works with standalone Agent() — no workflow required!
```

### Slide 11: Tool approval code — standalone agent
```
agent-framework

Defining tools that require approval

@tool(approval_mode="always_require")
def submit_expense_report(
  description: Annotated[str, "Description of the expense report"],
  total_amount: Annotated[str, "Total amount to reimburse"],
) -> str:
  """Submit an expense report. Requires manager approval."""
  return f"Expense report submitted: {description} for {total_amount}"

@tool(approval_mode="never_require")
def lookup_receipt(receipt_id: Annotated[str, "The receipt ID"]) -> dict:
  """Look up a receipt by ID."""
  return {"vendor": "Office Depot", "amount": "$142.50"}

approval_mode options:
  "always_require" — Always pause for approval
  "never_require"  — Never pause (default)

Full example: agent_tool_approval.py
```

### Slide 12: Handling approval — standalone agent
```
agent-framework

Handling approval requests with a standalone Agent

agent = Agent(client=client, name="ExpenseAgent",
  tools=[lookup_receipt, submit_expense_report])

result = await agent.run(query)

while len(result.user_input_requests) > 0:
  new_inputs = [query]
  for request in result.user_input_requests:
    print(f"Tool: {request.function_call.name}")
    print(f"Args: {request.function_call.arguments}")

    # Include the approval request in context
    new_inputs.append(Message("assistant", [request]))

    approved = input("Approve? (y/n): ") == "y"
    new_inputs.append(Message("user",
      [request.to_function_approval_response(approved)]))

  result = await agent.run(new_inputs)

💡 Same @tool decorator works in workflows too — see workflow_hitl_tool_approval.py

Full example: agent_tool_approval.py
```

### Slide 13: Section — Requests and Responses
```
Requests and Responses
https://learn.microsoft.com/agent-framework/workflows/requests-and-responses
```

### Slide 14: How request_info works
```
agent-framework

How requests and responses work
Executors can pause a workflow and ask for human input:

    Application code              Executor                 Human
        │                           │                        │
        │  workflow.run(msg)        │                        │
        ├─────────────────────────► │                        │
        │                           │  ctx.request_info()    │
        │  event.type ==            │                        │
        │  "request_info"           │                        │
        │ ◄─────────────────────────┤                        │
        │  (workflow pauses)        │                        │
        │                           │                        │
        │  prompt user ───────────────────────────────────►  │
        │                                                    │  answers
        │  ◄──────────────────────── input ──────────────────┤
        │                           │                        │
        │  workflow.run(            │                        │
        │    responses={            │                        │
        │      req_id: answer})     │                        │
        ├─────────────────────────► │                        │
        │                           │  @response_handler()   │
        │                           │  (workflow resumes)    │
        │                           ▼                        │

Speaker notes:
The request_info/response cycle is driven by application code:
  1. Executor calls ctx.request_info(request_data=..., response_type=str)
  2. Workflow emits WorkflowEvent with type="request_info"
  3. Application collects event, prompts user, gathers reply
  4. Application calls workflow.run(responses={request_id: reply})
  5. @response_handler receives the original request + user reply
```

### Slide 15: Simple chat — Workflow topology
```
Simple chat: Workflow topology

                          edge                 edge
   Input ──► [ChatCoordinator] ─────────► [ChatAgent] ──┐
          str       │          AgentExecutor    │         │
                    │          Request      LLM call     │
                    │                                    │
                    │◄───────────────────────────────────┘
                    │          AgentExecutor
                    │          Response (str)
               request_info ──────► 👤 Human
              (every turn)              │
           UserPrompt             answers (str)
                    │◄──────────────────┘
               yield_output
              (when "done")
                    │
                 Output

Speaker notes:
  "This diagram shows the most basic form of HITL routing: an unconditional pause.
  Notice the request_info call happens every single turn. More importantly, look at
  who makes the decision to stop. The human has two paths, one of which is typing 'done',
  which triggers yield_output. Because the LLM is just generating raw text, it has
  no way to reliably signal 'I am finished' to the workflow. So we have to put the
  burden of the exit condition on the human."
```

### Slide 16: Simple chat — Executor code (always ask)
```
agent-framework

Simple chat: Executor code (always ask)
After every agent response, pause and ask the human for the next message.
No structured outputs, no routing — pure HITL mechanics.

class ChatCoordinator(Executor):
  @handler
  async def on_agent_response(self, result: AgentExecutorResponse, ctx):
    # Always pause and ask the human
    await ctx.request_info(
      request_data=UserPrompt(message=result.agent_response.text),
      response_type=str)

  @response_handler
  async def on_human_reply(self, original_request, reply, ctx):
    if reply.strip().lower() == "done":
      await ctx.yield_output("Conversation ended.")
      return
    await ctx.send_message(AgentExecutorRequest(
      messages=[Message("user", text=reply)],
      should_respond=True))

Full example: workflow_hitl_requests.py
```

### Slide 16: Simple chat — Application code
```
agent-framework

Simple chat: Application code

stream = workflow.run("What are fun things to do in Seattle?",
                      stream=True)

while True:
  pending = {}
  async for event in stream:
    if event.type == "request_info":
      pending[event.request_id] = event.data

  if not pending:
    break

  for request_id, request in pending.items():
    print(f"Agent: {request.message}")
    reply = input("You (or 'done'): ")
    pending[request_id] = reply

  stream = workflow.run(stream=True, responses=pending)

Full example: workflow_hitl_requests.py

Speaker notes:
  "Why iterate over pending.items()?" — In this simple example there's always
  exactly one request per turn. But the loop is the correct general pattern because:
  (1) workflow.run(responses=...) expects a dict mapping request IDs to replies,
  (2) other HITL patterns can produce multiple requests per turn (e.g., an agent
  calling several approval-required tools at once, or concurrent executors each
  emitting a request). The loop costs two extra lines and teaches the right idiom.
```

### Slide 17: Trip planner — Workflow topology (structured)
```
Trip planner: Workflow topology (with structured outputs)

                          edge                    edge
   Input ──► [TripCoordinator] ──────────► [TripPlanner] ──┐
       str    │     ▲         AgentExecutor      │          │
              │     │         Request         LLM call     │
              │     │                    response_format=   │
              │     │                    PlannerOutput      │
              │     │◄─────────────────────────────────────┘
              │     │      AgentExecutorResponse
              │     │
              │     └──── 👤 Human answers (str)
              │                │
              │ .status        │ @response_handler
              │ (PlannerOutput)│ sends answer back
              │                │ to agent
         ┌────┴────────┐
    need_info      complete
         │              │
    request_info   yield_output
    (question ──► 👤)   │
                     Output

Speaker notes:
  "Contrast this with the previous topology. Here, we've moved the routing logic
  off the human and given it to the agent. Notice the diamond in the middle — the
  framework now inspects the agent's structured output status first. The workflow
  pauses for a request *only* if the LLM tells it to. And look at the human's role
  on the left: they just answer questions. The exit branch on the right is now
  controlled by the agent deciding it has gathered enough information to stop."
```

### Slide 18: Trip planner — Agent definition (structured outputs)
```
agent-framework

Trip planner: Agent definition
Define the routing states explicitly in the agent's schema.

class PlannerOutput(BaseModel):
    status: Literal["need_info", "complete"]
    question: str | None = None
    itinerary: str | None = None

planner_agent = Agent(
    name="TripPlanner",
    instructions=(
        "You are a helpful trip planner... "
        "Ask clarifying questions ONE AT A TIME... "
        "Once you have enough information, produce a final itinerary."
    ),
    client=client,
    default_options={"response_format": PlannerOutput},
)

Full example: workflow_hitl_requests_structured.py

Speaker notes:
  "Now let's look at the agent itself.
  We define a Pydantic model with two literal statuses: 'need_info' or 'complete'.
  By passing this as the response_format, we are forcing the LLM to categorize
  its own state. It will either ask a question, or provide the final itinerary.
  This gives us the reliable routing hooks you just saw in the diagram."
```

### Slide 19: Trip planner — Executor code (structured)
```
agent-framework

Trip planner: Executor code (with structured outputs)
Use structured outputs to let the agent decide when it has enough info.

class TripCoordinator(Executor):
  @handler
  async def on_agent_response(self, result: AgentExecutorResponse, ctx):
    response = result.agent_response.value
    if response.status == "need_info":
      await ctx.request_info(
        request_data=UserPrompt(message=response.question),
        response_type=str)
    else:
      await ctx.yield_output(response.itinerary)

  @response_handler
  async def on_human_answer(self, original_request, answer, ctx):
    await ctx.send_message(AgentExecutorRequest(
      messages=[Message("user", text=answer)],
      should_respond=True))

Full example: workflow_hitl_requests_structured.py
```

### Slide 20: Section — Checkpoints & Resuming
```
Checkpoints & Resuming
https://learn.microsoft.com/agent-framework/workflows/checkpoints
```

### Slide 21: Why checkpoints for HITL?
```
Why checkpoints for HITL workflows?

Without checkpoints:                    With checkpoints:

 Workflow pauses for approval           Workflow pauses for approval
 Human is offline                       Human is offline
 Process crashes or restarts            Checkpoint saved to disk  💾
 ❌ All progress lost!                  Process can safely exit

                                        ...hours later...

                                        New process starts
                                        Loads checkpoint from disk 📂
                                        Human provides approval
                                        ✅ Workflow resumes from where it left off

Checkpoints capture:
• Executor states  • Pending messages  • Pending requests  • Shared state
```

### Slide 22: Checkpoint lifecycle
```
Checkpoint lifecycle

  Process A                                         Process B
  ─────────                                         ─────────
  workflow.run(input)
       │
   [Executor] ──► [Agent] ──► [Executor]
       │
   ctx.request_info()
       │
   💾 Checkpoint saved
       │              ┌─────────────────────────────────┐
       ▼              │  checkpoints/                    │
   🚪 Process exits   │  ┌───────────┬────────────────┐  │
                      │  │ ID        │ Contains       │  │
                      │  ├───────────┼────────────────┤  │
                      │  │ abc-001   │ executor states│  │
                      │  │           │ pending reqs   │──────►  new_workflow.run(
                      │  │           │ messages       │  │        checkpoint_id="abc-001")
                      │  │           │ shared state   │  │            │
                      │  └───────────┴────────────────┘  │       📂 State restored
                      └─────────────────────────────────┘            │
                                                               🔄 re-emits request_info
                                                                     │
                                                               (normal HITL loop
                                                                from here on)

Speaker notes:
  "Here's what happens under the hood. Process A runs the workflow until it hits
  a request_info call. At that point, a checkpoint is saved to disk — that includes
  executor states, pending messages, and the pending request itself. Process A can
  now safely exit. Hours later, Process B starts up, creates a fresh workflow, and
  calls run with just the checkpoint ID. The framework restores all the state and
  re-emits the pending request_info event. From that point on, it's the same HITL
  loop we already saw — collect the request, prompt the user, call run(responses=...).
  The only new thing is that first call to restore from the checkpoint.

  In production, you'd also need your own table mapping users or sessions to
  their latest checkpoint ID — the framework stores the snapshots, but it's up
  to your app to know which checkpoint belongs to which user."
```

### Slide 23: Checkpoint code setup
```
agent-framework

Setting up checkpointed HITL workflows

from agent_framework import FileCheckpointStorage, WorkflowBuilder

checkpoint_storage = FileCheckpointStorage(storage_path="./checkpoints")

workflow = (WorkflowBuilder(
    start_executor=prepare_brief,
    checkpoint_storage=checkpoint_storage)
  .add_edge(prepare_brief, writer)
  .add_edge(writer, review_gateway)
  .add_edge(review_gateway, writer)    # revisions loop
  .build())

# Checkpoints are saved automatically at the end of each superstep.
# When a request_info is pending, the checkpoint status is
# "awaiting human response".

Full example: workflow_hitl_checkpoint.py
```

### Slide 23: Resuming from checkpoint
```
agent-framework

Resuming a workflow from a checkpoint

# Check for existing checkpoints on startup
checkpoints = await storage.list_checkpoints()

if checkpoints:
  # Resume from the latest checkpoint
  latest = sorted(checkpoints, key=lambda cp: cp.timestamp)[-1]
  workflow = create_workflow(checkpoint_storage=storage)

  # Framework restores state and re-emits pending request_info
  stream = workflow.run(
    checkpoint_id=latest.checkpoint_id,
    stream=True)

  # Same HITL loop as before — no special "resume" logic needed
  async for event in stream:
    if event.type == "request_info":
      # Prompt user, collect response...
    elif event.type == "output":
      print(f"Result: {event.data}")

Full example: workflow_hitl_checkpoint.py

Speaker notes:
  "Notice we don't need any special resume logic in the event loop.
  The framework re-emits the pending request_info, so your app picks it up
  the same way it would on the first run. The only new line is
  workflow.run(checkpoint_id=...) instead of workflow.run(message=...)."
```

### Slide 24: Saving executor state
```
agent-framework

Saving custom executor state in checkpoints

class ReviewGateway(Executor):
  def __init__(self, id: str):
    super().__init__(id=id)
    self._iteration = 0

  @handler
  async def on_agent_response(self, response, ctx):
    self._iteration += 1
    await ctx.request_info(
      request_data=HumanApprovalRequest(
        draft=response.agent_response.text,
        iteration=self._iteration),
      response_type=str)

  async def on_checkpoint_save(self) -> dict[str, Any]:
    return {"iteration": self._iteration}

  async def on_checkpoint_restore(self, state: dict[str, Any]) -> None:
    self._iteration = state.get("iteration", 0)

Full example: workflow_hitl_checkpoint.py

Speaker notes:
  "You only need to save state that changes during execution. Here, _iteration
  starts at zero and increments each time the agent produces a draft. If we don't
  checkpoint it, a resumed workflow would think it's on iteration zero again.
  But notice we don't save writer_id — that's a constructor parameter that never
  changes. When you resume, you rebuild the workflow from scratch with the same
  constructor args, so those values are already set. on_checkpoint_save and
  on_checkpoint_restore are only for runtime-mutated state that the constructor
  wouldn't know about."
```

### Slide 25: CheckpointStorage Protocol
```
Custom checkpoint storage

CheckpointStorage is a Protocol — implement these 6 methods for any backend:

  Method                        Purpose
  ─────────────────────────     ──────────────────────────────
  save(checkpoint)              Persist a snapshot, return ID
  load(checkpoint_id)           Restore a snapshot by ID
  delete(checkpoint_id)         Remove a snapshot
  list_checkpoints(name)        All snapshots for a workflow
  get_latest(name)              Most recent snapshot
  list_checkpoint_ids(name)     IDs only (lightweight)

  Built-in backends:
    • FileCheckpointStorage     JSON files on disk
    • InMemoryCheckpointStorage In-process dict (testing only)

  Custom backends:
    • PostgreSQL, Redis, Cosmos DB, blob storage, ...

Speaker notes:
  "The framework ships with two built-in backends: FileCheckpointStorage which
  writes JSON files to disk, and InMemoryCheckpointStorage which is just a dict
  in memory — great for tests, but obviously lost when the process exits.
  CheckpointStorage is a Protocol, so you can implement these six methods for
  any backend you want. Let's see what that looks like with PostgreSQL."
```

### Slide 26: Designing checkpoint storage
```
Designing your checkpoint storage

Schema example (PostgreSQL):

  id              workflow_name      timestamp                   data
  ─────────────   ────────────────   ─────────────────────────   ──────────────
  abc-001         content_review     2026-03-03T14:22:01+00:00   {"executor_...
  abc-002         content_review     2026-03-03T14:22:03+00:00   {"executor_...
  def-001         trip_planner:42    2026-03-03T15:10:44+00:00   {"executor_...

Design decisions to consider:

  Question                          Considerations
  ────────────────────────          ──────────────────────────────────
  How to scope checkpoints?         Per workflow name? Per user/session?
                                    e.g. workflow_name = "review:{user_id}"

  How long to keep them?            Prune after completion? TTL? Keep N latest?

  How large are they?               Checkpoints include full message history.
                                    Long conversations = large JSONB blobs.

  Who can access them?              Row-level security? Separate tables per tenant?

Speaker notes:
  "Before you write code, think about your schema. At minimum you need an ID,
  the workflow name for filtering, and a timestamp for ordering. The data column
  stores the encoded checkpoint as JSON — the framework handles serialization for you.
  The harder questions are around scoping and lifecycle. In a multi-user app, do you
  embed the user ID in the workflow name, or add a user_id column? How do you prune
  old checkpoints? These are application-level decisions the framework doesn't make
  for you."
```

### Slide 27: Custom checkpoint storage — PostgreSQL example
```
agent-framework

Custom checkpoint storage: PostgreSQL example

class PostgresCheckpointStorage:
  def __init__(self, conninfo: str):
    self._conninfo = conninfo
    # CREATE TABLE IF NOT EXISTS workflow_checkpoints (
    #   id TEXT PRIMARY KEY, workflow_name TEXT,
    #   timestamp TEXT, data JSONB)

  async def save(self, checkpoint: WorkflowCheckpoint) -> str:
    encoded = encode_checkpoint_value(checkpoint.to_dict())
    await conn.execute(
      """INSERT INTO workflow_checkpoints (id, workflow_name, timestamp, data)
         VALUES (%s, %s, %s, %s)
         ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data""",
      (checkpoint.checkpoint_id, checkpoint.workflow_name,
       checkpoint.timestamp, json.dumps(encoded)))
    return checkpoint.checkpoint_id

  async def load(self, checkpoint_id: str) -> WorkflowCheckpoint:
    row = await conn.execute(
      "SELECT data FROM workflow_checkpoints WHERE id = %s",
      (checkpoint_id,)).fetchone()
    return WorkflowCheckpoint.from_dict(
      decode_checkpoint_value(row["data"]))

  # list_checkpoints, get_latest, delete = just SQL queries!

# Drop-in replacement — no other code changes needed:
storage = PostgresCheckpointStorage(conninfo=POSTGRES_URL)
workflow = WorkflowBuilder(..., checkpoint_storage=storage).build()

Full example: workflow_hitl_checkpoint_pg.py

Speaker notes:
  "With PostgreSQL, the implementation is even simpler than Redis. save is a
  single INSERT ON CONFLICT. load is a SELECT by ID. list_checkpoints, get_latest,
  and delete are all one-line SQL queries — no manual indexing needed. The database
  handles ordering by timestamp, filtering by workflow name, and atomic updates.
  It's a drop-in replacement for FileCheckpointStorage."
```

### Slide 26: Section — Handoff with HITL
```
Handoff with HITL
https://learn.microsoft.com/agent-framework/workflows/orchestrations/handoff
```

### Slide 26: Recap Handoff orchestration
```
Recap: Handoff orchestration

                                       Agent B
    start agent
                              handoff
     Agent A                              Agent C

No edges defined — routing emerges from conversation state.

Unlike other orchestrations, Handoff is inherently interactive:
• When an agent doesn't handoff, it requests user input
• Workflow emits HandoffAgentUserRequest events
• Application must respond for the workflow to continue
• Use .with_autonomous_mode() to skip user input
```

### Slide 27: Handoff — Interactive user input
```
agent-framework

Handoff: Interactive user input (no autonomous mode)
Without .with_autonomous_mode(), the framework pauses for user input.

# No .with_autonomous_mode() — pauses for user input between turns
workflow = (HandoffBuilder(
    name="customer_support",
    participants=[triage, order_agent, return_agent])
  .with_start_agent(triage)
  .build())

# Event loop handles HandoffAgentUserRequest events
for request_event in request_events:
  if isinstance(request_event.data, HandoffAgentUserRequest):
    # Show agent's response
    for msg in request_event.data.agent_response.messages[-3:]:
      print(f"{msg.author_name}: {msg.text}")

    user_input = input("You: ")
    if user_input == "exit":
      responses[id] = HandoffAgentUserRequest.terminate()
    else:
      responses[id] = HandoffAgentUserRequest.create_response(user_input)

Full example: workflow_hitl_handoff.py

Speaker notes:
  "This is the simplest form of HITL with Handoff. Without autonomous mode,
  every time an agent responds without handing off, the framework emits a
  HandoffAgentUserRequest. Your app shows the agent's message and prompts
  the user. You can also call terminate() to end the workflow early.
  This is the default behavior — autonomous mode is the opt-in."
```

### Slide 28: Handoff — Adding tool approval
```
agent-framework

Handoff: Adding tool approval
Combine user input with tool approval in the same event loop.

@tool(approval_mode="always_require")
def process_refund(order_number: str) -> str:
  """Process a refund for a given order."""
  return f"Refund processed for order {order_number}."

# Same HandoffBuilder, but agents have approval-required tools
# The event loop handles BOTH types of requests:
for request_event in request_events:
  if isinstance(request_event.data, HandoffAgentUserRequest):
    # Agent needs user input (same as before)
    responses[id] = HandoffAgentUserRequest.create_response(user_input)

  elif isinstance(request_event.data, Content):
    # Agent wants to call a tool requiring approval
    print(f"Tool: {request_event.data.function_call.name}")
    approved = input("Approve? (y/n): ") == "y"
    responses[id] = request_event.data.to_function_approval_response(approved)

Full example: workflow_hitl_handoff_approval.py

Speaker notes:
  "You can combine user input and tool approval in the same handoff workflow.
  The event loop just checks the type of each request: HandoffAgentUserRequest
  for conversational input, or Content with a function_approval_request for
  tool gating. This is the same @tool(approval_mode='always_require') decorator
  we saw earlier — it works the same way inside a handoff workflow."
```

### Slide 29: Next steps / resources
```
Next steps                      Register:
                                https://aka.ms/PythonAgents/series

Watch past recordings:          Join office hours after each session in Discord:
aka.ms/pythonagents/resources   aka.ms/pythonai/oh

    Feb 24: Building your first agent in Python
    Feb 25: Adding context and memory to agents
    Feb 26: Monitoring and evaluating agents
    Mar 3: Building your first AI-driven workflows
    Mar 4: Orchestrating advanced multi-agent workflows
    Mar 5: Adding a human-in-the-loop to workflows ← Today
```
