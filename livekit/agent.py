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


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
            "You were created as a demo to showcase the capabilities of LiveKit's agents framework."
        ),
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")
    
    
    async def connect_with_flask_server(text):
        """ Function connect with flask server to validate the response."""

        API_URL = "http://127.0.0.1:5000"
        FALLBACK_MESSAGE = "Something went wrong, please ask another question!"
        
        text = " ".join([d async for d in text])
        payload = {"text": text}
        headers = {'Content-Type': 'application/json'}
        
        # Sending a POST request to the Flask API
        response = requests.post(f"{API_URL}/trim-response", headers=headers, data=json.dumps(payload))
        try:
            if response.status_code == 200:
                data = response.json()
                return data.get('message', FALLBACK_MESSAGE)
            else:
                return FALLBACK_MESSAGE
        except Exception as e:
            return FALLBACK_MESSAGE

    
    async def before_tts_cb(assistant: VoicePipelineAgent, text: str | AsyncIterable[str]):
        if type(text) is not str:
            response = await connect_with_flask_server(text)
            await assistant.say(response, allow_interruptions=True)
            return ""
        return text

    # This project is configured to use Deepgram STT, OpenAI LLM and Cartesia TTS plugins
    # Other great providers exist like Cerebras, ElevenLabs, Groq, Play.ht, Rime, and more
    # Learn more and pick the best one for your app:
    # https://docs.livekit.io/agents/plugins
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
    usage_collector = metrics.UsageCollector()

    @agent.on("metrics_collected")
    def on_metrics_collected(agent_metrics: metrics.AgentMetrics):
        metrics.log_metrics(agent_metrics)
        usage_collector.collect(agent_metrics)

    agent.start(ctx.room, participant)

    # The agent should be polite and greet the user when it joins :)
    await agent.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
