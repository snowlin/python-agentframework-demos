"""Workflow de soporte al cliente con handoff, entrada de usuario HITL y aprobación de herramientas.

Demuestra: HandoffBuilder, HandoffAgentUserRequest, FunctionApprovalRequestContent,
bucle de eventos combinado de entrada de usuario + aprobación de herramientas,
y @tool(approval_mode="always_require").

Un agente de triaje dirige problemas de clientes a agentes especialistas (reembolsos,
seguimiento de pedidos). El agente de reembolsos usa una herramienta que requiere
aprobación humana antes de ejecutarse. El workflow es interactivo: cuando un agente
no transfiere, solicita entrada del usuario.

Ejecutar:
    uv run examples/spanish/workflow_hitl_handoff_approval.py
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

# Configura el cliente según el host de la API
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


# --- Herramientas ---


@tool(approval_mode="always_require")
def process_refund(
    order_number: Annotated[str, "Order number to process refund for"],
    amount: Annotated[str, "Refund amount"],
    reason: Annotated[str, "Reason for the refund"],
) -> str:
    """Process a refund for a given order number."""
    return f"Reembolso de {amount} procesado exitosamente para el pedido {order_number}. Razón: {reason}"


@tool(approval_mode="never_require")
def check_order_status(
    order_number: Annotated[str, "Order number to check status for"],
) -> str:
    """Check the status of a given order number."""
    return f"El pedido {order_number} está siendo procesado y se enviará en 2 días hábiles."


# --- Agentes ---

triage = Agent(
    client=client,
    name="triage_agent",
    instructions=(
        "Eres un agente de triaje de servicio al cliente. Escucha los problemas del cliente y determina "
        "si necesitan ayuda con reembolsos o seguimiento de pedidos. Dirígelos al especialista apropiado."
    ),
    description="Triage agent that handles general inquiries.",
)

refund_agent = Agent(
    client=client,
    name="refund_agent",
    instructions=(
        "Eres un especialista en reembolsos. Ayuda a los clientes con solicitudes de reembolso. "
        "Sé empático y pide números de pedido si no los proporcionan. "
        "Cuando el usuario confirme que quiere un reembolso y proporcione los detalles del pedido, "
        "llama a process_refund para registrar la solicitud."
    ),
    description="Agent that handles refund requests.",
    tools=[process_refund],
)

order_agent = Agent(
    client=client,
    name="order_agent",
    instructions=(
        "Eres un especialista en seguimiento de pedidos. Ayuda a los clientes a rastrear sus pedidos. "
        "Pide números de pedido y proporciona actualizaciones de envío."
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


# --- Principal ---


async def main() -> None:
    """Ejecuta el workflow de handoff con entrada de usuario y aprobación de herramientas."""
    initial_message = "Hola, mi pedido 12345 llegó dañado. Necesito un reembolso."
    print(f"👤 Cliente: {initial_message}\n")

    # Ejecución inicial
    request_events: list[WorkflowEvent] = []
    async for event in workflow.run(initial_message, stream=True):
        if event.type == "request_info":
            request_events.append(event)

    # Bucle interactivo: maneja tanto entrada de usuario como solicitudes de aprobación de herramientas
    while request_events:
        responses: dict[str, Any] = {}

        for request_event in request_events:
            if isinstance(request_event.data, HandoffAgentUserRequest):
                # El agente necesita entrada del usuario
                agent_response = request_event.data.agent_response
                if agent_response.messages:
                    for msg in agent_response.messages[-3:]:
                        if msg.text:
                            speaker = msg.author_name or msg.role
                            print(f"🤖 {speaker}: {msg.text}")

                user_input = input("\n👤 Tú: ").strip()
                if user_input.lower() in ("exit", "salir", "quit"):
                    responses[request_event.request_id] = HandoffAgentUserRequest.terminate()
                else:
                    responses[request_event.request_id] = HandoffAgentUserRequest.create_response(user_input)

            elif isinstance(request_event.data, Content) and request_event.data.type == "function_approval_request":
                # El agente quiere llamar una herramienta que requiere aprobación
                func_call = request_event.data.function_call
                if func_call is None:
                    raise ValueError("Falta la información de la llamada a función")
                args = func_call.parse_arguments() or {}
                print(f"\n🔒 Aprobación de herramienta solicitada: {func_call.name}")
                print(f"   Argumentos: {json.dumps(args, indent=2)}")
                approval = input("   ¿Aprobar/Approve? (y/n): ").strip().lower() == "y"
                print(f"   {'✅ Aprobado' if approval else '❌ Rechazado'}\n")
                responses[request_event.request_id] = request_event.data.to_function_approval_response(
                    approved=approval
                )

        # Envía respuestas y recopila nuevas solicitudes
        request_events = []
        async for event in workflow.run(responses=responses, stream=True):
            if event.type == "request_info":
                request_events.append(event)
            elif event.type == "output":
                print("\n✅ ¡Workflow completado!")

    if async_credential:
        await async_credential.close()


if __name__ == "__main__":
    if "--devui" in sys.argv:
        from agent_framework.devui import serve

        serve(entities=[workflow], port=8099, auto_open=True)
    else:
        asyncio.run(main())
