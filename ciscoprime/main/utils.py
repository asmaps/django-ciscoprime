from django.conf import settings

import re
import requests


def api_request(url):
    out = dict()
    r = requests.get(
        url,
        verify=False,
        auth=(settings.API_USER, settings.API_PASSWORD))
    try:
        out['json_response'] = r.json()
    except ValueError:
        out['error'] = 'An error occured. Please check back again later.'
        out['error_detail'] = 'Unexpected response from controller. Not json!'
    return out


rogue_reg = re.compile(".*Rogue AP '(?P<mac>.*)' with SSID '(?P<ssid>[^']*)' (and channel number '(?P<channel>.*)' )?is detected by AP '(?P<ap>.*)' Radio type '(?P<radio_type>.*)' with RSSI '(?P<rssi>[^']*)'( and SNR '(?P<snr>.*)')?.*")


def analyze_rogue_alert_msg(msg):
    rogue = dict()
    m = rogue_reg.match(msg)
    if m:
        return {
            'ssid': m.group('ssid'),
            'mac': m.group('mac'),
            'channel': m.group('channel'),
            'detecting_ap': m.group('ap'),
            'radio_type': m.group('radio_type'),
            'rssi': m.group('rssi')
        }
    else:
        raise ValueError('Message "%s" not decodable' % msg)
