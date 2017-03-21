try:
    import requests
except ImportError:
    from ..Utils import pip_install

    pip_install('requests')

from WebHookRelayAlarm import WebHookRelayAlarm
