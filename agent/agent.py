import json
import logging
import os
from typing import AsyncIterable

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
    metrics,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, silero, turn_detector, rime, speechmatics
import requests

load_dotenv(dotenv_path='.env.local')
logger = logging.getLogger("voice-assistant")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def trim_response(text):
    """ send the response to flask server and get an appropriate response"""
   
    text = "".join([d async for d in text])
    payload = {"text": text}
    headers = {'Content-Type': 'application/json'}
    
    # Sending a POST request to the Flask API
    response = requests.post(
        "http://127.0.0.1:5000/flask-api", 
        headers=headers, 
        data=json.dumps(payload)
    )
    error_message = "Something went wrong, i'm happy to give answer of any other question!"
    try:
        if response.status_code == 200:
            data = response.json()
            return data.get('message', error_message)
        else:
            return error_message
    except Exception as e:
        return error_message


async def before_tts_cb(assistant: VoicePipelineAgent, text: str | AsyncIterable[str]):
    if type(text) != str:
        response = await trim_response(text)
        await assistant.say(response, allow_interruptions=True)
        return ""
    return text

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation."
        ),
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")


    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=speechmatics.STT(),
        llm=openai.LLM.with_groq(api_key=GROQ_API_KEY),
        tts=rime.TTS(),
        before_tts_cb=before_tts_cb,
        turn_detector=turn_detector.EOUModel(),
        # minimum delay for endpointing, used when turn detector believes the user is done with their turn
        min_endpointing_delay=0.5,
        # maximum delay for endpointing, used when turn detector does not believe the user is done with their turn
        max_endpointing_delay=5.0,
        chat_ctx=initial_ctx,
    )

    agent.start(ctx.room, participant)

    usage_collector = metrics.UsageCollector()

    @agent.on("metrics_collected")
    def _on_metrics_collected(mtrcs: metrics.AgentMetrics):
        metrics.log_metrics(mtrcs)
        usage_collector.collect(mtrcs)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: ${summary}")

    ctx.add_shutdown_callback(log_usage)

    await agent.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            ws_url=os.getenv("LIVEKIT_URL")
        ),
    )