"""Native Home Assistant Assist intents for BTDoor Security+."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import DOMAIN, SERVICE_OPEN_GATE

INTENT_OPEN_GATE = "BTDoorOpenGate"
DEFAULT_LANGUAGE = "en"

VOICE_RESPONSES = {'en': ('BTDoor Security+ is not available.', 'More than one BTDoor gate is configured. Use the named gate entity.', 'Opening the gate.', 'Home Assistant Assist voice command'), 'it': ('BTDoor Security+ non è disponibile.', 'Sono configurati più cancelli BTDoor. Usa il nome specifico del cancello.', 'Apro il cancello.', 'Comando vocale Home Assistant Assist'), 'fr': ('BTDoor Security+ n’est pas disponible.', 'Plusieurs portails BTDoor sont configurés. Utilisez le nom du portail.', 'J’ouvre le portail.', 'Commande vocale Home Assistant Assist'), 'de': ('BTDoor Security+ ist nicht verfügbar.', 'Mehrere BTDoor-Tore sind konfiguriert. Verwende den Namen des Tores.', 'Das Tor wird geöffnet.', 'Home Assistant Assist Sprachbefehl'), 'es': ('BTDoor Security+ no está disponible.', 'Hay más de una puerta BTDoor configurada. Usa el nombre de la puerta.', 'Abriendo la puerta.', 'Comando de voz de Home Assistant Assist'), 'nl': ('BTDoor Security+ is niet beschikbaar.', 'Er zijn meerdere BTDoor-poorten geconfigureerd. Gebruik de naam van de poort.', 'De poort wordt geopend.', 'Home Assistant Assist-spraakopdracht'), 'pt': ('O BTDoor Security+ não está disponível.', 'Há mais de um portão BTDoor configurado. Use o nome do portão.', 'A abrir o portão.', 'Comando de voz do Home Assistant Assist'), 'pl': ('BTDoor Security+ jest niedostępny.', 'Skonfigurowano więcej niż jedną bramę BTDoor. Użyj nazwy bramy.', 'Otwieram bramę.', 'Polecenie głosowe Home Assistant Assist'), 'cs': ('BTDoor Security+ není dostupný.', 'Je nakonfigurováno více bran BTDoor. Použijte název brány.', 'Otevírám bránu.', 'Hlasový příkaz Home Assistant Assist'), 'da': ('BTDoor Security+ er ikke tilgængelig.', 'Der er konfigureret mere end én BTDoor-port. Brug portens navn.', 'Åbner porten.', 'Home Assistant Assist-stemmekommando'), 'sv': ('BTDoor Security+ är inte tillgänglig.', 'Flera BTDoor-grindar är konfigurerade. Använd grindens namn.', 'Öppnar grinden.', 'Home Assistant Assist-röstkommando'), 'nb': ('BTDoor Security+ er ikke tilgjengelig.', 'Flere BTDoor-porter er konfigurert. Bruk navnet på porten.', 'Åpner porten.', 'Home Assistant Assist-talekommando'), 'fi': ('BTDoor Security+ ei ole käytettävissä.', 'Useita BTDoor-portteja on määritetty. Käytä portin nimeä.', 'Avataan portti.', 'Home Assistant Assist -äänikomento'), 'ja': ('BTDoor Security+ は利用できません。', '複数の BTDoor ゲートが設定されています。ゲート名を指定してください。', 'ゲートを開けます。', 'Home Assistant Assist 音声コマンド'), 'ko': ('BTDoor Security+를 사용할 수 없습니다.', '여러 BTDoor 게이트가 구성되어 있습니다. 게이트 이름을 사용하세요.', '게이트를 엽니다.', 'Home Assistant Assist 음성 명령'), 'zh-Hans': ('BTDoor Security+ 不可用。', '配置了多个 BTDoor 大门。请使用大门名称。', '正在打开大门。', 'Home Assistant Assist 语音命令'), 'zh-Hant': ('BTDoor Security+ 無法使用。', '已設定多個 BTDoor 大門。請使用大門名稱。', '正在開啟大門。', 'Home Assistant Assist 語音命令')}

def _language(intent_obj: intent.Intent) -> str:
    requested = getattr(intent_obj, "language", None) or intent_obj.hass.config.language
    if requested in VOICE_RESPONSES:
        return requested
    base = str(requested).split("-", 1)[0]
    return base if base in VOICE_RESPONSES else DEFAULT_LANGUAGE


class BTDoorOpenGateIntent(intent.IntentHandler):
    intent_type = INTENT_OPEN_GATE
    description = "Open a BTicino gate configured through BTDoor Security+"

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        response = intent_obj.create_response()
        language = _language(intent_obj)
        unavailable, ambiguous, opening, reason = VOICE_RESPONSES[language]
        entries = [entry for entry in intent_obj.hass.config_entries.async_entries(DOMAIN) if getattr(entry, "runtime_data", None) is not None]
        if not entries:
            response.async_set_speech(unavailable)
            return response
        if len(entries) > 1:
            response.async_set_speech(ambiguous)
            return response
        result = await intent_obj.hass.services.async_call(
            DOMAIN, SERVICE_OPEN_GATE,
            {"entry_id": entries[0].entry_id, "reason": reason, "source": "assist"},
            blocking=True, context=intent_obj.context, return_response=True,
        )
        item = (result or {}).get(entries[0].entry_id, {})
        if not item.get("success"):
            response.async_set_speech(unavailable)
            return response
        response.async_set_speech(opening)
        return response


def async_register_voice_intents(hass: HomeAssistant) -> None:
    marker = f"{DOMAIN}_voice_intents_registered"
    if hass.data.get(marker):
        return
    intent.async_register(hass, BTDoorOpenGateIntent())
    hass.data[marker] = True
