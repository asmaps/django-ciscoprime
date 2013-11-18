from django.conf import settings

import re
import requests


def api_request(url):
    print 'api_request "%s"' % url
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


def best_rssi_for_correlated(correlated):
    r = api_request(
            'https://140.221.243.254/webacs/api/v1/data/Events.json?.full=true&correlated="%d"&severity=ne("CLEARED")' % correlated)
    ap = None
    if r.get('json_response'):
        for entity in r['json_response']['queryResponse']['entity']:
            try:
                event = analyze_rogue_alert_msg(entity['eventsDTO']['description'])
                if not ap:
                    ap = event
                elif int(event['rssi']) > int(ap['rssi']):
                    print "changing %s to %s" % (unicode(ap), unicode(event))
                    ap = event
            except ValueError:
                #FIXME
                print 'Non decodable rogue message "%s".'
    return ap

