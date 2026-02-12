import os
import contextlib
from fastapi import FastAPI
from config.setting import env
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # os.environ["LANGSMITH_API_KEY"] = env.langsmith_api_key
    # os.environ["LANGSMITH_ENDPOINT"] = env.langsmith_endpoint
    # os.environ["LANGSMITH_TRACING_V2"] = env.langsmith_tracing
    # os.environ["LANGSMITH_PROJECT"] = env.langsmith_project
    # async with contextlib.AsyncExitStack() as stack:
        # await stack.enter_async_context(mcp_server.session_manager.run())
        
    # Phoenix.init()

    yield

app = FastAPI(lifespan=lifespan)
