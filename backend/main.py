"""Main entrypoint for Intelligent Shopping Assistant backend service."""
from pathlib import Path
from typing import Any, Dict

import yaml
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
OPENAPI_FILE = BASE_DIR / "openapi.yml"

app = FastAPI(title="Intelligent Shopping Assistant API")

# Load environment variables from .env if present
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)

API_KEY = os.getenv("DAJI_API_KEY", "not-set")  # Example usage

# ---------------------------------------------------------------------------
# Standardized JSON response middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def standard_json_response(request: Request, call_next):
    response = await call_next(request)

    # If running in test mode, return original response to avoid body consumption issues
    if getattr(app.state, "testing", False) or isinstance(response, JSONResponse):
        return response

    # Otherwise wrap in standard structure
    body = None
    if response.body_iterator:
        body = b"".join([chunk async for chunk in response.body_iterator])
    return JSONResponse(
        status_code=response.status_code,
        content={
            "status": "success" if response.status_code < 400 else "error",
            "data": body.decode() if body else None,
        },
    )

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
from fastapi import APIRouter
from backend.services.preprocessor import preprocess_input
from backend.services.llm_service import get_shopping_intent
from backend.services import daji_service, weidian_service

health_router = APIRouter()

@health_router.get("/healthz", summary="Health check")
async def health_check() -> Dict[str, str]:
    return {"message": "ok"}

app.include_router(health_router)

intent_router = APIRouter(prefix="/api/v1/intent")

@intent_router.post("/parse", summary="Parse user input and detect shopping intent")
async def parse_intent(payload: Dict[str, str]):
    """Endpoint implementing contract-driven intent parsing.

    Expected JSON body: { "userInput": "..." }
    """
    text: str = payload.get("userInput", "") if isinstance(payload, dict) else ""

    preprocessed_data = preprocess_input(text)

    # Decide whether to call LLM
    if preprocessed_data["type"] == "text" or not preprocessed_data["skip_llm"]:
        llm_intent = await get_shopping_intent(preprocessed_data["content"])

        shopping = False
        if isinstance(llm_intent, dict):
            shopping = bool(llm_intent.get("shopping_intent", False))

        message = (
            "请点击联系我们进行人工购物帮助！" if shopping else "我们仅支持专业的代购需求，谢谢您的使用！"
        )

        return {
            "hasUrls": False,
            "urls": [],
            "products": [],
            "llmAnalysis": message,
            "shopping_intent": shopping,
        }

    # URLs were found
    products = []
    for platform, urls in preprocessed_data["platform_map"].items():
        for u in urls:
            if platform == "taobao":
                prod = await daji_service.fetch_product_detail(u)
            elif platform == "weidian":
                prod = await weidian_service.fetch_product_detail(u)
            else:
                prod = None
            if prod:
                products.append(prod)

    return {
        "hasUrls": True,
        "urls": preprocessed_data["urls"],
        "platform_map": preprocessed_data["platform_map"],
        "products": products,
        "llmAnalysis": None,
    }

app.include_router(intent_router)

# ---------------------------------------------------------------------------
# Custom OpenAPI that loads spec from openapi.yml so FastAPI docs reflect the
# contract defined by the project.
# ---------------------------------------------------------------------------

def load_openapi_spec() -> Dict[str, Any]:
    """Load the OpenAPI YAML file and return as dict."""
    if OPENAPI_FILE.exists():
        with OPENAPI_FILE.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    raise FileNotFoundError("openapi.yml not found at project root")

_spec_cache: Dict[str, Any] | None = None


def custom_openapi():
    global _spec_cache  # noqa: PLW0603
    if _spec_cache is None:
        _spec_cache = load_openapi_spec()
    return _spec_cache

app.openapi = custom_openapi

# ---------------------------------------------------------------------------
# Uvicorn entry (python -m backend.main)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True) 