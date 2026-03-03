"""Customer support handoff workflow with HITL user input and tool approval.

Demonstrates: HandoffBuilder, HandoffAgentUserRequest, FunctionApprovalRequestContent,
combined user-input + tool-approval event loop, and @tool(approval_mode="always_require").

A triage agent routes customer issues to specialist agents (refund, order tracking).
The refund agent uses a tool that requires human approval before executing.
The workflow is interactive: when an agent doesn't hand off, it requests user input.

Run:
    uv run examples/workflow_hitl_handoff_approval.py
"""

import asyncio
import json
import os
import sys
from typing import Annotated, Any

from agent_framework import (
    Agent,
    Content,
    WorkflowEvent,
    tool,
)
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import HandoffAgentUserRequest, HandoffBuilder
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

load_dotenv(override=True)
API_HOST = os.getenv("API_HOST", "github")

# Configure the chat client based on the API host
async_credential = None
if API_HOST == "azure":
    async_credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(async_credential, "https://cognitiveservices.azure.com/.default")
    client = OpenAIChatClient(
        base_url=f"{os.environ['AZURE_OPENAI_ENDPOINT']}/openai/v1/",
        api_key=token_provider,
        model_id=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
    )
elif API_HOST == "github":
    client = OpenAIChatClient(
        base_url="https://models.github.ai/inference",
        api_key=os.environ["GITHUB_TOKEN"],
        model_id=os.getenv("GITHUB_MODEL", "openai/gpt-5-mini"),
    )
else:
    client = OpenAIChatClient(
        api_key=os.environ["OPENAI_API_KEY"], model_id=os.environ.get("OPENAI_MODEL", "gpt-5-mini")
    )


# --- Tools ---


@tool(approval_mode="always_require")
def process_refund(
    order_number: Annotated[str, "Order number to process refund for"],
    amount: Annotated[str, "Refund amount"],
    reason: Annotated[str, "Reason for the refund"],
) -> str:
    """Process a refund for a given order number."""
    return f"Refund of {amount} processed successfully for order {order_number}. Reason: {reason}"


@tool(approval_mode="never_require")
def check_order_status(
    order_number: Annotated[str, "Order number to check status for"],
) -> str:
    """Check the status of a given order number."""
    return f"Order {order_number} is currently being processed and will ship in 2 business days."


# --- Agents ---

triage = Agent(
    client=client,
    name="triage_agent",
    instructions=(
        "You are a customer service triage agent. Listen to customer issues and determine "
        "if they need refund help or order tracking. Route them to the appropriate specialist."
    ),
    description="Triage agent that handles general inquiries.",
)

refund_agent = Agent(
    client=client,
    name="refund_agent",
    instructions=(
        "You are a refund specialist. Help customers with refund requests. "
        "Be empathetic and ask for order numbers if not provided. "
        "When the user confirms they want a refund and supplies order details, "
        "call process_refund to record the request."
    ),
    description="Agent that handles refund requests.",
    tools=[process_refund],
)

order_agent = Agent(
    client=client,
    name="order_agent",
    instructions=(
        "You are an order tracking specialist. Help customers track their orders. "
        "Ask for order numbers and provide shipping updates."
    ),
    description="Agent that handles order tracking and shipping issues.",
    tools=[check_order_status],
)


# --- Workflow ---

workflow = (
    HandoffBuilder(
        name="customer_support",
        participants=[triage, refund_agent, order_agent],
        termination_condition=lambda conversation: (
            len(conversation) > 0 and "goodbye" in conversation[-1].text.lower()
        ),
    )
    .with_start_agent(triage)
    .build()
)


# --- Main ---


async def main() -> None:
    """Run the handoff workflow with user input and tool approval."""
    initial_message = "Hi, my order 12345 arrived damaged. I need a refund."
    print(f"👤 Customer: {initial_message}\n")

    # Initial run
    request_events: list[WorkflowEvent] = []
    async for event in workflow.run(initial_message, stream=True):
        if event.type == "request_info":
            request_events.append(event)

    # Interactive loop: handle both user input and tool approval requests
    while request_events:
        responses: dict[str, Any] = {}

        for request_event in request_events:
            if isinstance(request_event.data, HandoffAgentUserRequest):
                # Agent needs user input
                agent_response = request_event.data.agent_response
                if agent_response.messages:
                    for msg in agent_response.messages[-3:]:
                        if msg.text:
                            speaker = msg.author_name or msg.role
                            print(f"🤖 {speaker}: {msg.text}")

                user_input = input("\n👤 You: ").strip()
                if user_input.lower() in ("exit", "quit"):
                    responses[request_event.request_id] = HandoffAgentUserRequest.terminate()
                else:
                    responses[request_event.request_id] = HandoffAgentUserRequest.create_response(user_input)

            elif isinstance(request_event.data, Content) and request_event.data.type == "function_approval_request":
                # Agent wants to call a tool requiring approval
                func_call = request_event.data.function_call
                if func_call is None:
                    raise ValueError("Function call information is missing")
                args = func_call.parse_arguments() or {}
                print(f"\n🔒 Tool approval requested: {func_call.name}")
                print(f"   Arguments: {json.dumps(args, indent=2)}")
                approval = input("   Approve? (y/n): ").strip().lower() == "y"
                print(f"   {'✅ Approved' if approval else '❌ Rejected'}\n")
                responses[request_event.request_id] = request_event.data.to_function_approval_response(
                    approved=approval
                )

        # Send responses and collect new requests
        request_events = []
        async for event in workflow.run(responses=responses, stream=True):
            if event.type == "request_info":
                request_events.append(event)
            elif event.type == "output":
                print("\n✅ Workflow completed!")

    if async_credential:
        await async_credential.close()


if __name__ == "__main__":
    if "--devui" in sys.argv:
        from agent_framework.devui import serve

        serve(entities=[workflow], port=8099, auto_open=True)
    else:
        asyncio.run(main())
