import os
import sys
import traceback
from typing import Any

import runpod
from runpod import RunPodLogger

from engine import LlamaCPPEngine, LlamaCPPOpenAIEngine
from utils import JobInput

DEFAULT_MAX_CONCURRENCY = 1

max_concurrency = int(os.getenv("MAX_CONCURRENCY", DEFAULT_MAX_CONCURRENCY))
log = RunPodLogger()
llama_engine = LlamaCPPEngine()
openai_engine = LlamaCPPOpenAIEngine()


async def handler(job: Any):
    try:
        job_input = JobInput(job.get("input") or {})
        engine = openai_engine if job_input.openai_route else llama_engine

        async for batch in engine.generate(job_input):
            yield batch
    except Exception as exc:
        message = str(exc)
        log.error(f"Error during inference: {message}")
        log.error(traceback.format_exc())
        if "cuda" in message.lower():
            sys.exit(1)
        yield {"error": message}


runpod.serverless.start(
    {
        "handler": handler,
        "concurrency_modifier": lambda _x: max_concurrency,
        "return_aggregate_stream": True,
    }
)
