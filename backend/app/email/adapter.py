import logging
from typing import Protocol

from app.config import settings

logger = logging.getLogger(__name__)

# Captured codes for mock provider (tests/dev)
mock_sent_codes: dict[str, str] = {}


class EmailAdapter(Protocol):
    async def send_verification_code(self, to: str, code: str) -> None: ...


class MockEmailAdapter:
    async def send_verification_code(self, to: str, code: str) -> None:
        mock_sent_codes[to] = code
        logger.info("[mock-email] verification code for %s: %s", to, code)


class SmtpEmailAdapter:
    async def send_verification_code(self, to: str, code: str) -> None:
        import aiosmtplib
        from email.message import EmailMessage

        if not settings.smtp_host:
            raise RuntimeError("SMTP_HOST não configurado")

        msg = EmailMessage()
        msg["From"] = settings.smtp_from
        msg["To"] = to
        msg["Subject"] = "Código de verificação — WFRP Solo"
        body = (
            f"Seu código de verificação WFRP Solo: {code}\n\n"
            f"Válido por 15 minutos.\n"
        )
        msg.set_content(body)

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            start_tls=settings.smtp_use_tls,
        )


def get_email_adapter() -> EmailAdapter:
    provider = settings.email_provider.lower()
    if provider == "smtp":
        return SmtpEmailAdapter()
    return MockEmailAdapter()
