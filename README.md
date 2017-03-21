WebHookRelay is a 3rd party extension of [PokeAlarm](https://github.com/kvangent/PokeAlarm) that allows you to buffer and relay notifications to an external webhook.

<b>Installation</b>
1. Copy the contents of the src folder into the PokeAlarm installation directory:
    \PokeAlarm\PokeAlarm\Manager.py
    \PokeAlarm\PokeAlarm\WebHookRelay\__init__.py
    \PokeAlarm\PokeAlarm\WebHookRelay\WebHookRelayAlarm.py
    
2. Set your webhook address and activate the service (See PokeAlarm\alarms.json.example):
{
    "active": "True",
    "type": "webhookrelay",
    "webhook_address": "YOUR_WEBHOOK_URL",
    "requests_per_second": 1
}
