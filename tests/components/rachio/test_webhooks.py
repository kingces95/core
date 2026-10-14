"""Tests for Rachio webhooks."""

from unittest.mock import patch

from homeassistant.components.rachio.const import CONF_WEBHOOK_URL_BASE, DOMAIN
from homeassistant.components.rachio.webhooks import (
    async_get_or_create_registered_webhook_id_and_url,
)
from homeassistant.const import CONF_API_KEY, CONF_WEBHOOK_ID
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def test_custom_webhook_url_base(hass: HomeAssistant) -> None:
    """Test a custom webhook public base URL is used."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "api-key", CONF_WEBHOOK_ID: "webhook-id"},
        options={
            CONF_WEBHOOK_URL_BASE: "https://example.com/home/rachio",
        },
    )
    entry.add_to_hass(hass)

    with (
        patch(
            "homeassistant.components.rachio.webhooks.cloud.async_active_subscription",
            return_value=True,
        ),
        patch(
            "homeassistant.components.rachio.webhooks.cloud.async_create_cloudhook"
        ) as create_cloudhook,
    ):
        webhook_url = await async_get_or_create_registered_webhook_id_and_url(
            hass, entry
        )

    assert webhook_url == "https://example.com/home/rachio/webhook-id"
    create_cloudhook.assert_not_called()


async def test_default_webhook_url(hass: HomeAssistant) -> None:
    """Test the Home Assistant webhook URL is used by default."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "api-key", CONF_WEBHOOK_ID: "webhook-id"},
    )
    entry.add_to_hass(hass)

    with (
        patch(
            "homeassistant.components.rachio.webhooks.cloud.async_active_subscription",
            return_value=False,
        ),
        patch(
            "homeassistant.components.rachio.webhooks.webhook.async_generate_url",
            return_value="https://example.com/api/webhook/webhook-id",
        ) as generate_url,
    ):
        webhook_url = await async_get_or_create_registered_webhook_id_and_url(
            hass, entry
        )

    assert webhook_url == "https://example.com/api/webhook/webhook-id"
    generate_url.assert_called_once_with(hass, "webhook-id")
