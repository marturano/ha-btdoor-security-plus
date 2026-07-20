"""Config flow for BTDoor Security+."""

from __future__ import annotations

from pathlib import Path
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .cloud import (
    BticinoCloudAuthenticationError,
    BticinoCloudClient,
    BticinoCloudConnectionError,
    BticinoCloudError,
    PlantGateway,
    generate_id_device,
)
from .const import (
    CONF_CA_CHAIN_PATH,
    CONF_CERTIFICATE_NOT_AFTER,
    CONF_CLIENT_CERT_PATH,
    CONF_CLIENT_KEY_PATH,
    CONF_DEVICE_NAME,
    CONF_EMAIL,
    CONF_GATEWAY_ID,
    CONF_GATEWAY_NAME,
    CONF_ID_DEVICE,
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_PLANT_NAME,
    CONF_PORT,
    CONF_SERVER,
    CONF_SIP_ACCOUNT,
    CONF_SIP_PASSWORD,
    CONF_VERIFY_SERVER,
    DEFAULT_DEVICE_NAME,
    DEFAULT_PORT,
    DEFAULT_SERVER,
    DEFAULT_VERIFY_SERVER,
    CONF_DEBUG_MODE,
    CONF_DEVELOPER_MODE,
    DEFAULT_DEBUG_MODE,
    DEFAULT_DEVELOPER_MODE,
    CONF_SHOW_CLOUD_STATUS,
    CONF_SHOW_SIP_MONITOR,
    CONF_SHOW_CALL_MONITOR,
    CONF_SHOW_MEDIA_MONITOR,
    CONF_SHOW_ADVANCED_DIAGNOSTICS,
    DEFAULT_SHOW_CLOUD_STATUS,
    DEFAULT_SHOW_SIP_MONITOR,
    DEFAULT_SHOW_CALL_MONITOR,
    DEFAULT_SHOW_MEDIA_MONITOR,
    DEFAULT_SHOW_ADVANCED_DIAGNOSTICS,
    DEBUG_MODE_OFF,
    DEBUG_MODE_SUPPORT,
    DEBUG_MODE_DEEP,
    DOMAIN,
)
from .sip_client import (
    BticinoSipAuthenticationError,
    BticinoSipClient,
    BticinoSipConnectionError,
    BticinoSipError,
)

_LOGGER = logging.getLogger(__name__)


class BticinoDoorEntryConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a BTDoor Security+ config flow."""

    VERSION = 2
    MINOR_VERSION = 0

    def __init__(self) -> None:
        self._credentials: dict[str, Any] = {}
        self._gateways: dict[str, PlantGateway] = {}
        self._id_device = generate_id_device()
        self._reconfigure_entry = None

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the support-debug options flow."""
        return BTDoorOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Authenticate with MyHomeWeb and discover gateways."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self._credentials = dict(user_input)
            try:
                gateways = await self._async_discover(user_input)
            except BticinoCloudAuthenticationError:
                errors["base"] = "invalid_cloud_auth"
            except BticinoCloudConnectionError:
                errors["base"] = "cannot_connect_cloud"
            except BticinoCloudError:
                errors["base"] = "cloud_error"
            except Exception as err:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during MyHomeWeb configuration", exc_info=err)
                errors["base"] = "unknown"
            else:
                self._gateways = {item.gateway_id: item for item in gateways}
                if not gateways:
                    errors["base"] = "no_gateways"
                elif len(gateways) == 1:
                    return await self._async_finish(gateways[0])
                else:
                    return await self.async_step_select_gateway()

        return self.async_show_form(
            step_id="user",
            data_schema=_cloud_schema(user_input),
            errors=errors,
        )

    async def async_step_select_gateway(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select one gateway when the account has multiple gateways."""
        if user_input is not None:
            return await self._async_finish(
                self._gateways[str(user_input[CONF_GATEWAY_ID])]
            )
        options = [
            {"value": gateway_id, "label": item.label}
            for gateway_id, item in self._gateways.items()
        ]
        return self.async_show_form(
            step_id="select_gateway",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_GATEWAY_ID): SelectSelector(
                        SelectSelectorConfig(
                            options=options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Reconfigure cloud credentials and registered DeviceName."""
        entry = self._get_reconfigure_entry()
        self._reconfigure_entry = entry
        self._id_device = str(entry.data.get(CONF_ID_DEVICE) or generate_id_device())
        errors: dict[str, str] = {}
        if user_input is not None:
            self._credentials = dict(user_input)
            try:
                gateways = await self._async_discover(user_input)
                current_gateway = str(entry.data.get(CONF_GATEWAY_ID, ""))
                selection = next(
                    (item for item in gateways if item.gateway_id == current_gateway),
                    None,
                )
                if selection is None:
                    raise BticinoCloudError("Configured gateway not found")
                data = await self._async_provision_and_validate(selection)
            except BticinoCloudAuthenticationError:
                errors["base"] = "invalid_cloud_auth"
            except BticinoCloudConnectionError:
                errors["base"] = "cannot_connect_cloud"
            except BticinoSipAuthenticationError:
                errors["base"] = "invalid_auth"
            except BticinoSipConnectionError:
                errors["base"] = "cannot_connect"
            except (BticinoCloudError, BticinoSipError):
                errors["base"] = "provisioning_error"
            except Exception as err:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during MyHomeWeb configuration", exc_info=err)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(selection.gateway_id)
                self._abort_if_unique_id_mismatch(reason="wrong_gateway")
                return self.async_update_and_abort(
                    entry,
                    title="Bticino DS+ Suite",
                    data_updates=data,
                )

        defaults = {
            CONF_EMAIL: entry.data.get(CONF_EMAIL, ""),
            CONF_DEVICE_NAME: entry.data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
            CONF_SERVER: entry.data.get(CONF_SERVER, DEFAULT_SERVER),
            CONF_VERIFY_SERVER: entry.data.get(
                CONF_VERIFY_SERVER, DEFAULT_VERIFY_SERVER
            ),
        }
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_cloud_schema(user_input or defaults),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Start reauthentication after cloud credentials are rejected."""
        self._credentials = dict(entry_data)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm new cloud password."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        if user_input is not None:
            merged = dict(entry.data)
            merged.update(user_input)
            self._credentials = merged
            self._id_device = str(
                entry.data.get(CONF_ID_DEVICE) or generate_id_device()
            )
            try:
                gateways = await self._async_discover(merged)
                selection = next(
                    (
                        item
                        for item in gateways
                        if item.gateway_id == str(entry.data[CONF_GATEWAY_ID])
                    ),
                    None,
                )
                if selection is None:
                    raise BticinoCloudError("Configured gateway not found")
                data = await self._async_provision_and_validate(selection)
            except BticinoCloudAuthenticationError:
                errors["base"] = "invalid_cloud_auth"
            except BticinoCloudConnectionError:
                errors["base"] = "cannot_connect_cloud"
            except (BticinoCloudError, BticinoSipError):
                errors["base"] = "provisioning_error"
            else:
                return self.async_update_and_abort(entry, title="Bticino DS+ Suite", data_updates=data)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL, default=entry.data.get(CONF_EMAIL, "")
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.EMAIL)
                    ),
                    vol.Required(CONF_PASSWORD): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    async def _async_discover(
        self, user_input: dict[str, Any]
    ) -> list[PlantGateway]:
        client = BticinoCloudClient(
            async_get_clientsession(self.hass),
            email=str(user_input[CONF_EMAIL]),
            password=str(user_input[CONF_PASSWORD]),
        )
        await client.async_login()
        return await client.async_list_gateways()

    async def _async_finish(self, selection: PlantGateway) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        await self.async_set_unique_id(selection.gateway_id)
        self._abort_if_unique_id_configured()
        try:
            data = await self._async_provision_and_validate(selection)
        except BticinoCloudAuthenticationError:
            errors["base"] = "invalid_cloud_auth"
        except BticinoCloudConnectionError:
            errors["base"] = "cannot_connect_cloud"
        except BticinoSipAuthenticationError:
            errors["base"] = "invalid_auth"
        except BticinoSipConnectionError:
            errors["base"] = "cannot_connect"
        except (BticinoCloudError, BticinoSipError):
            errors["base"] = "provisioning_error"
        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("Unexpected error while provisioning BTDoor Security+", exc_info=err)
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(
                title="Bticino DS+ Suite",
                data=data,
            )
        return self.async_show_form(
            step_id="user",
            data_schema=_cloud_schema(self._credentials),
            errors=errors,
        )

    async def _async_provision_and_validate(
        self, selection: PlantGateway
    ) -> dict[str, Any]:
        cloud = BticinoCloudClient(
            async_get_clientsession(self.hass),
            email=str(self._credentials[CONF_EMAIL]),
            password=str(self._credentials[CONF_PASSWORD]),
        )
        await cloud.async_login()
        storage_dir = Path(
            self.hass.config.path("custom_components", DOMAIN, "certificate", selection.gateway_id)
        )
        provisioned = await cloud.async_provision(
            selection=selection,
            device_name=str(
                self._credentials.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME)
            ),
            id_device=self._id_device,
            storage_dir=storage_dir,
        )
        data: dict[str, Any] = {
            CONF_EMAIL: str(self._credentials[CONF_EMAIL]),
            CONF_PASSWORD: str(self._credentials[CONF_PASSWORD]),
            CONF_DEVICE_NAME: provisioned.device_name,
            CONF_PLANT_ID: provisioned.plant_id,
            CONF_PLANT_NAME: provisioned.plant_name,
            CONF_GATEWAY_ID: provisioned.gateway_id,
            CONF_GATEWAY_NAME: provisioned.gateway_name,
            CONF_ID_DEVICE: provisioned.id_device,
            CONF_SIP_ACCOUNT: provisioned.sip_account,
            CONF_SIP_PASSWORD: provisioned.sip_password,
            CONF_CLIENT_CERT_PATH: provisioned.client_cert_path,
            CONF_CLIENT_KEY_PATH: provisioned.client_key_path,
            CONF_CERTIFICATE_NOT_AFTER: provisioned.certificate_not_after,
            CONF_SERVER: str(self._credentials.get(CONF_SERVER, DEFAULT_SERVER)),
            CONF_PORT: DEFAULT_PORT,
            CONF_VERIFY_SERVER: bool(
                self._credentials.get(CONF_VERIFY_SERVER, DEFAULT_VERIFY_SERVER)
            ),
        }
        if provisioned.ca_chain_path:
            data[CONF_CA_CHAIN_PATH] = provisioned.ca_chain_path
        await _validate_sip(data)
        return data



class BTDoorOptionsFlow(OptionsFlow):
    """Configure module visibility, diagnostics and developer tools."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_SHOW_CLOUD_STATUS, default=options.get(CONF_SHOW_CLOUD_STATUS, DEFAULT_SHOW_CLOUD_STATUS)): BooleanSelector(),
                vol.Required(CONF_SHOW_SIP_MONITOR, default=options.get(CONF_SHOW_SIP_MONITOR, DEFAULT_SHOW_SIP_MONITOR)): BooleanSelector(),
                vol.Required(CONF_SHOW_CALL_MONITOR, default=options.get(CONF_SHOW_CALL_MONITOR, DEFAULT_SHOW_CALL_MONITOR)): BooleanSelector(),
                vol.Required(CONF_SHOW_MEDIA_MONITOR, default=options.get(CONF_SHOW_MEDIA_MONITOR, DEFAULT_SHOW_MEDIA_MONITOR)): BooleanSelector(),
                vol.Required(CONF_SHOW_ADVANCED_DIAGNOSTICS, default=options.get(CONF_SHOW_ADVANCED_DIAGNOSTICS, DEFAULT_SHOW_ADVANCED_DIAGNOSTICS)): BooleanSelector(),
                vol.Required(CONF_DEVELOPER_MODE, default=options.get(CONF_DEVELOPER_MODE, DEFAULT_DEVELOPER_MODE)): BooleanSelector(),
                vol.Required(CONF_DEBUG_MODE, default=options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE)): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            DEBUG_MODE_OFF,
                            DEBUG_MODE_SUPPORT,
                            DEBUG_MODE_DEEP,
                        ],
                        translation_key=CONF_DEBUG_MODE,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }),
        )

def _cloud_schema(values: dict[str, Any] | None) -> vol.Schema:
    values = values or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_EMAIL, default=values.get(CONF_EMAIL, "")
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.EMAIL)),
            vol.Required(CONF_PASSWORD): TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
            vol.Required(
                CONF_DEVICE_NAME,
                default=values.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
            vol.Optional(
                CONF_SERVER, default=values.get(CONF_SERVER, DEFAULT_SERVER)
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
            vol.Optional(
                CONF_VERIFY_SERVER,
                default=values.get(CONF_VERIFY_SERVER, DEFAULT_VERIFY_SERVER),
            ): BooleanSelector(),
        }
    )


async def _validate_sip(data: dict[str, Any]) -> None:
    client = BticinoSipClient(
        sip_account=data[CONF_SIP_ACCOUNT],
        sip_password=data[CONF_SIP_PASSWORD],
        gateway_id=data[CONF_GATEWAY_ID],
        client_cert_path=data[CONF_CLIENT_CERT_PATH],
        client_key_path=data[CONF_CLIENT_KEY_PATH],
        server=data.get(CONF_SERVER, DEFAULT_SERVER),
        port=int(data.get(CONF_PORT, DEFAULT_PORT)),
        verify_server=bool(data.get(CONF_VERIFY_SERVER, DEFAULT_VERIFY_SERVER)),
    )
    await client.async_test_connection()
