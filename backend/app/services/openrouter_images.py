import base64
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_IMAGES_URL = "https://openrouter.ai/api/v1/images"

WFRP_STYLE_PREFIX = (
    "Dark fantasy illustration, Warhammer Fantasy Roleplay style, "
    "grim medieval atmosphere, muted palette, painterly: "
)

COMPOSITION_HINTS: dict[str, str] = {
    "cena": "wide cinematic scene, ",
    "personagem": "character portrait, ",
    "mapa": "wide landscape map view, fantasy cartography, ",
    "item": "isolated item on dark background, ",
}

PROBE_PROMPT = "minimal dark fantasy landscape, validation probe"
PROBE_IMAGE_TYPE = "cena"


class OpenRouterNotConfigured(Exception):
    pass


class OpenRouterGenerationError(Exception):
    pass


def is_quota_or_credit_error(exc: BaseException) -> bool:
    if isinstance(exc, OpenRouterNotConfigured):
        return True
    if isinstance(exc, OpenRouterGenerationError):
        msg = str(exc).lower()
        if any(token in msg for token in ("quota", "credit", "insufficient", "payment required")):
            return True
        if "402" in msg or "429" in msg:
            return True
    return False


async def probe_image_credits(
    client: "OpenRouterImagesClient | None" = None,
) -> bool:
    client = client or OpenRouterImagesClient()
    if not client.enabled:
        return False
    try:
        await client.generate_image(PROBE_PROMPT, PROBE_IMAGE_TYPE)
        return True
    except Exception:
        return False


class OpenRouterImagesClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = (api_key if api_key is not None else settings.openrouter_api_key).strip()
        self.model = (model or settings.openrouter_image_model).strip()

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _build_prompt(self, description: str, image_type: str) -> str:
        hint = COMPOSITION_HINTS.get(image_type, "")
        return WFRP_STYLE_PREFIX + hint + description

    async def generate_image(self, description: str, image_type: str = "cena") -> bytes:
        if not self.enabled:
            raise OpenRouterNotConfigured("OPENROUTER_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.api_base_url.rstrip("/"),
            "X-Title": "WFRP Solo",
        }
        payload = {
            "model": self.model,
            "prompt": self._build_prompt(description, image_type),
            "output_format": "jpeg",
            "aspect_ratio": "16:9",
        }

        async with httpx.AsyncClient(timeout=60.0) as http:
            try:
                response = await http.post(OPENROUTER_IMAGES_URL, headers=headers, json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code == 402:
                    raise OpenRouterGenerationError(
                        "OpenRouter payment required / credits insufficient (HTTP 402)"
                    ) from exc
                if status_code == 429:
                    raise OpenRouterGenerationError(
                        "OpenRouter quota/rate limit (HTTP 429)"
                    ) from exc
                raise OpenRouterGenerationError(f"OpenRouter HTTP {status_code}") from exc
            data = response.json()

        items = data.get("data") or []
        if not items:
            error_msg = data.get("error") or data
            msg_lower = str(error_msg).lower()
            if any(token in msg_lower for token in ("quota", "credit", "insufficient")):
                logger.warning("OpenRouter quota/credits error in response body")
            raise OpenRouterGenerationError(f"OpenRouter response missing image data: {error_msg}")

        image_b64 = items[0].get("b64_json")
        if not image_b64:
            raise OpenRouterGenerationError("OpenRouter response missing b64_json")

        try:
            return base64.b64decode(image_b64)
        except Exception as exc:
            raise OpenRouterGenerationError("Invalid base64 image from OpenRouter") from exc
