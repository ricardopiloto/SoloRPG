import logging
from pathlib import Path

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

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


class CloudflareNotConfigured(Exception):
    pass


class CloudflareGenerationError(Exception):
    pass


class CloudflareWorkersAIClient:
    def __init__(
        self,
        account_id: str | None = None,
        api_token: str | None = None,
        model: str | None = None,
    ):
        self.account_id = (account_id if account_id is not None else settings.cloudflare_account_id).strip()
        self.api_token = (api_token if api_token is not None else settings.cloudflare_api_token).strip()
        self.model = (model or settings.cloudflare_ai_model).strip()

    @property
    def enabled(self) -> bool:
        return bool(self.account_id and self.api_token)

    def _build_prompt(self, description: str, image_type: str) -> str:
        hint = COMPOSITION_HINTS.get(image_type, "")
        return WFRP_STYLE_PREFIX + hint + description

    async def generate_image(self, description: str, image_type: str = "cena") -> bytes:
        if not self.enabled:
            raise CloudflareNotConfigured("CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN not configured")

        url = (
            f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}"
            f"/ai/run/{self.model}"
        )
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": self._build_prompt(description, image_type),
            "steps": 4,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code == 429:
                    raise CloudflareGenerationError(
                        "Cloudflare quota/tokens esgotados (HTTP 429)"
                    ) from exc
                raise CloudflareGenerationError(
                    f"Cloudflare HTTP {status_code}"
                ) from exc
            data = response.json()

        if not data.get("success", True):
            errors = data.get("errors", [])
            codes = [e.get("code") for e in errors if isinstance(e, dict)]
            if 10000 in codes:
                logger.warning("Cloudflare quota esgotada (success:false, code 10000)")
            raise CloudflareGenerationError(f"Cloudflare API error: {errors}")

        result = data.get("result") or {}
        image_b64 = result.get("image")
        if not image_b64:
            raise CloudflareGenerationError("Cloudflare response missing image data")

        import base64

        try:
            return base64.b64decode(image_b64)
        except Exception as exc:
            raise CloudflareGenerationError("Invalid base64 image from Cloudflare") from exc
