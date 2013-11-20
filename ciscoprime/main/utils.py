from django.conf import settings

import re
import requests

from .models import RogueAP, TrackedRogue


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
        rogue = {
            'ssid': m.group('ssid'),
            'mac': m.group('mac'),
            'channel': m.group('channel'),
            'detecting_ap': m.group('ap'),
            'radio_type': m.group('radio_type'),
            'rssi': m.group('rssi'),
        }
        (rap, created) = RogueAP.objects.get_or_create(mac=rogue['mac'], defaults={'correlated': 0, 'ssid': rogue['ssid']})
        if not rogue['ssid'] and not rogue['ssid'] == rap.ssid:
            TrackedRogue.objects.create(ap=rap, additional_info='Changed ssid from "%s" to "%s"' % (rap.ssid, rogue['ssid']))
            rap.ssid = rogue['ssid']
        rap.save()
        rogue['rogue_obj'] = rap
        rogue['tracked_rogue_count'] = rap.trackedrogue_set.all().count()
        return rogue
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

