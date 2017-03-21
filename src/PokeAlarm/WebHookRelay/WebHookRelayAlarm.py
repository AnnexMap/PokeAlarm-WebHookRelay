# Standard Library Imports
import logging
import requests

from datetime import datetime

# 3rd Party Imports
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, get_static_map_url

log = logging.getLogger('WebHookRelay')
try_sending = Alarm.try_sending
replace = Alarm.replace

#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class WebHookRelayAlarm(Alarm):

    _defaults = {
        'pokemon': {
            'username': "<pkmn>"
        },
        'pokestop': {
            'username': "Pokestop"
        },
        'gym': {
            'username': "<new_team> Gym Alerts"
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Service Info
        self.__requests_per_second = settings['requests_per_second']
        self.__webhook_address = settings['webhook_address']
        self.__startup_message = settings.get('startup_message', "True")
        self.__map = settings.get('map', {})
        self.__statup_list = settings.get('startup_list', "true")

        # Set Alerts        
        self.__pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.set_alert(settings.get('gym', {}), self._defaults['gym'])

		# Setup buffer
        self.refresh_buffer()
                
        log.info("WebHookRelay Alarm initialized.")

    # Establish connection with WebHookRelay
    def connect(self):
        pass

    # Send a message letting the channel know that this alarm has started
    def startup_message(self):
        if self.__startup_message:
            args = {
                'url': self.__webhook_address,
                'payload': {
                    'username': 'PokeAlarm',
                    'content': 'PokeAlarm activated!'
                }
            }
            #try_sending(log, self.connect, "WebHookRelay", self.send_webhook, args)
            log.info("Startup message sent!")
        
    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'webhook_address': settings.get('webhook_address', self.__webhook_address)
        }
        return alert

    # Send Alert to WebHookRelay
    def send_alert(self, alert, info):
        args = { 
            'webhook_address': alert['webhook_address'],
            'info': info
        }
        try_sending(log, self.connect, "WebHookRelay", self.send_webhook, args)

    def send_webhook(self, **args):
        log.debug(args)
        
        data = {
            'move_1': args['info']['quick_id'],
            'move_2': args['info']['charge_id'],
            'disappear_time': (args['info']['disappear_time'] - datetime(1970, 1, 1)).total_seconds(),
            'verified': 'false',
            'weight': args['info']['weight'],
            'pokemon_id': args['info']['pkmn_id'],
            'seconds_until_despawn': 2668,
            'individual_stamina': args['info']['sta'],
            'spawnpoint_id': '549aaab52b9',
            'individual_defense': args['info']['def'],
            'longitude': args['info']['lat'],
            'height': args['info']['height'],
            'time_until_hidden_ms': 975775121,
            'last_modified_time': 1489377876590,
            'gender': 1,
            'latitude': args['info']['lat'],
            'individual_attack': args['info']['atk'],
            'spawn_start': 2123,
            'encounter_id': args['info']['id'],
            'spawn_end': 2941
        }
        self.__poke_buffer.append(data)
        try:
            buffer_size = (len(self.__poke_buffer)/float((datetime.now()-self.__last_send).total_seconds() + 0.0000001))/self.__requests_per_second
            log.debug("buffer size: {}".format(buffer_size))
            if len(self.__poke_buffer) > buffer_size:
                log.info("Sending: {} pokemon".format(len(self.__poke_buffer)))
                requests.post(self.__webhook_address, json=self.__poke_buffer, timeout=(None, 1))
                # Refresh buffer
                self.refresh_buffer()
        except requests.exceptions.ReadTimeout:
            log.debug('Response timeout on webhook endpoint %s', self.__webhook_address)
        except requests.exceptions.RequestException as e:
            log.debug("WebHookRelay error was found: \n{}".format(e))

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    def refresh_buffer(self):
        self.__poke_buffer=[]
        self.__last_send = datetime.now()
