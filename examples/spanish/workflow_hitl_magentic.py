"""Orquestación Magentic con revisión de plan HITL antes de la ejecución.

Demuestra: MagenticBuilder(enable_plan_review=True), MagenticPlanReviewRequest,
event_data.approve() / event_data.revise(feedback), y streaming de salida del agente.

Un agente manager coordina a un investigador y un analista para completar una tarea
de investigación. Antes de ejecutar el plan, el manager lo presenta al humano para
revisión. El humano puede aprobar el plan o dar retroalimentación para revisarlo.

Ejecutar:
    uv run examples/spanish/workflow_hitl_magentic.py
"""

import asyncio
import json
import os
from typing import cast

from agent_framework import (
    Agent,
    AgentResponseUpdate,
    MagenticPlanReviewRequest,
    Message,
    WorkflowEvent,
)
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import MagenticBuilder
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


# --- Agentes ---

researcher_agent = Agent(
    name="ResearcherAgent",
    description="Specialist in research and information gathering",
    instructions=(
        "Eres un Investigador. Encuentras información y proporcionas resúmenes factuales. "
        "No realices análisis cuantitativo — deja eso al analista."
    ),
    chat_client=client,
)

analyst_agent = Agent(
    name="AnalystAgent",
    description="Specialist in data analysis and quantitative reasoning",
    instructions=(
        "Eres un Analista. Tomas los hallazgos de investigación y realizas análisis cuantitativo, "
        "creas comparaciones y produces recomendaciones estructuradas."
    ),
    chat_client=client,
)

manager_agent = Agent(
    name="MagenticManager",
    description="Orchestrator that coordinates the research and analysis workflow",
    instructions="Coordinas un equipo para completar tareas complejas de investigación de manera eficiente.",
    chat_client=client,
)


# --- Principal ---


async def main() -> None:
    """Ejecuta el workflow Magentic con revisión de plan HITL."""
    workflow = MagenticBuilder(
        participants=[researcher_agent, analyst_agent],
        manager_agent=manager_agent,
        enable_plan_review=True,
        max_round_count=10,
        max_stall_count=1,
        max_reset_count=2,
    ).build()

    task = (
        "Compara los pros y contras de tres frameworks web populares de Python "
        "(Django, Flask y FastAPI) para construir una API REST. "
        "Considera rendimiento, facilidad de uso, soporte de la comunidad y capacidades asíncronas. "
        "Proporciona una recomendación para una startup pequeña que construye su primera API."
    )

    print(f"📋 Tarea: {task}\n")

    pending_request: WorkflowEvent | None = None
    pending_responses: dict | None = None
    output_event: WorkflowEvent | None = None

    while not output_event:
        if pending_responses is not None:
            stream = workflow.run(responses=pending_responses)
        else:
            stream = workflow.run_stream(task)

        last_message_id: str | None = None
        async for event in stream:
            if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
                message_id = event.data.message_id
                if message_id != last_message_id:
                    if last_message_id is not None:
                        print("\n")
                    print(f"🤖 {event.executor_id}: ", end="", flush=True)
                    last_message_id = message_id
                print(event.data, end="", flush=True)

            elif event.type == "request_info" and event.request_type is MagenticPlanReviewRequest:
                pending_request = event

            elif event.type == "output":
                output_event = event

        pending_responses = None

        # Maneja la solicitud de revisión del plan
        if pending_request is not None:
            event_data = cast(MagenticPlanReviewRequest, pending_request.data)

            print("\n\n" + "=" * 60)
            print("📝 REVISIÓN DE PLAN SOLICITADA")
            print("=" * 60)

            if event_data.current_progress is not None:
                print("\nProgreso actual:")
                print(json.dumps(event_data.current_progress.to_dict(), indent=2))

            print(f"\nPlan propuesto:\n{event_data.plan.text}\n")
            print("Por favor proporciona tu retroalimentación (presiona Enter para aprobar/approve):")

            reply = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            if reply.strip() == "":
                print("✅ Plan aprobado.\n")
                pending_responses = {pending_request.request_id: event_data.approve()}
            else:
                print("📝 Plan revisado por el humano.\n")
                pending_responses = {pending_request.request_id: event_data.revise(reply)}
            pending_request = None

    # Salida final
    output_messages = cast(list[Message], output_event.data)
    final_output = output_messages[-1].text if output_messages else "Sin salida"
    print(f"\n\n{'=' * 60}")
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    print(final_output)

    if async_credential:
        await async_credential.close()


if __name__ == "__main__":
    asyncio.run(main())
