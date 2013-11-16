from django.conf import settings

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
