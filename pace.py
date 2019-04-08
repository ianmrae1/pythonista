#!/usr/bin/env python3

try:
    import clipboard
    clippy = True
except ImportError:
    clippy = False

import json
import math
import time

from stravalib import Client

CONFIG_FILE = 'strava_conf.json'

DEFAULT_DICT = \
    { 'client_id'     : '34162',
      'client_secret' : '15ae57df4a739e19ee800ff0457dcc0125ba69b6',
      'access_token'  : '1a190b07fb8ffc0dc548df92413f0fcfb57ef935',
      'expires_at'  : '0',
      'refresh_token' : 'e1a7674e170866644d368e232c1b2cb985f28d5f' }

def save_config(conf):
    with open(CONFIG_FILE, 'w') as outf:
        json.dump(conf, outf)

def load_config():
    try:
        with open(CONFIG_FILE) as inf:
            new_dict = json.load(inf)
    except FileNotFoundError:
        new_dict = DEFAULT_DICT.copy()
        save_config(new_dict)
    return new_dict

settings = load_config()
client = Client()

if time.time() > int(settings['expires_at']):
    print("Renewing tokens")
    refresh_response = client.refresh_access_token(client_id=settings['client_id'], client_secret=settings['client_secret'], refresh_token=settings['refresh_token'])
    settings['refresh_token'] = refresh_response['refresh_token']
    settings['access_token'] = refresh_response['access_token']
    settings['expires_at'] = refresh_response['expires_at']
    save_config(settings)
else:
    client.access_token = settings['access_token']
    client.refresh_token = settings['refresh_token']
    client.expires_at = settings['expires_at']

activities = client.get_activities(limit=10)

for activity in activities:
    if activity.type == 'Run':
        ms = activity.average_speed
        km = activity.distance/1000
        mile = km * 0.621371

        km_pace = 1000 / (ms * 60)
        sec_km, min_km = math.modf(km_pace)
        sec_km = sec_km * 60

        mile_pace = km_pace / 0.621371
        sec_mile, min_mile = math.modf(mile_pace)
        sec_mile = sec_mile * 60
        
        line1 = "Your most recent run was %.2f kilometers at %d:%02d minutes per kilometer.\r\n<br>" % (km, min_km, sec_km)
        line2 = "That's %.2f miles at %d:%02d minutes per mile.\r\n" % (mile, min_mile, sec_mile)
        
        if clippy:
            clipboard.set(line1 + line2)
        else:
            print(line1, line2)
        break

