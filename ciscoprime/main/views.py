from django.views.generic import TemplateView
from django.conf import settings

from braces.views import LoginRequiredMixin
import requests
import pprint
import re

from .utils import api_request


class RoguesView(TemplateView):
    template_name = 'main/rogues.html'

    def get_context_data(self, **kwargs):
        context = super(RoguesView, self).get_context_data(**kwargs)

        #rogue APs
        context['rogues'] = list()
        rogues = list()
        r = api_request(
            'https://140.221.243.254/webacs/api/v1/data/Alarms.json?category.value="Rogue AP"&condition.value="UNCLASSIFIED_ROGUE_AP_DETECTED"&severity=ne("CLEARED")&.full=true')
        if r.get('json_response'):
            context['rogues_count'] = r['json_response']['queryResponse']['@count']
            
            reg = re.compile(".*Rogue AP '(?P<mac>.*)' with SSID '(?P<ssid>[^']*)' (and channel number '(?P<channel>.*)' )?is detected by AP '(?P<ap>.*)' Radio type '(?P<radio_type>.*)' with RSSI '(?P<rssi>.*)'.*")
            
            for entity in r['json_response']['queryResponse']['entity']:
                print entity['alarmsDTO']['message']
                m = reg.match(entity['alarmsDTO']['message'])
                print m
                if m:
                    rogue = {
                        'ssid': m.group('ssid'),
                        'mac': m.group('mac'),
                        'channel': m.group('channel'),
                        'detecting_ap': m.group('ap'),
                        'radio_type': m.group('radio_type'),
                        'rssi': m.group('rssi')
                    }
                    rogues.append(rogue)
                    #exclude duplicates
                    a = []
            for r in rogues:
                if not r['ssid'] in a:
                    context['rogues'].append(r)
                    a.append(r['ssid'])
        return context


class OverviewView(TemplateView):
    template_name = 'main/overview.html'

    def get_context_data(self, **kwargs):
        context = super(OverviewView, self).get_context_data(**kwargs)
        #controller summary
        context['ctrl'] = dict()
        context['ctrl']['response'] = api_request(
            'https://140.221.243.254/webacs/api/v1/data/WlanControllers/2285283/.json')
        if context['ctrl']['response'].get('json_response'):
            context['ctrl']['entity'] = context['ctrl']['response']['json_response']['queryResponse']['entity'][0]

        #client count
        context['clients'] = dict()
        context['clients']['response'] = api_request(
            'https://140.221.243.254/webacs/api/v1/data/Clients.json?status="ASSOCIATED"')
        if context['clients']['response'].get('json_response'):
            context['clients']['count'] = context['clients']['response']['json_response']['queryResponse']['@count']

        #ap stats
        context['ap'] = dict()
        context['ap']['highest_client_count_aps'] = list()
        r = api_request(
            'https://140.221.243.254/webacs/api/v1/data/AccessPoints.json?.sort=-clientCount&.full=true')
        if r.get('json_response'):
            for i in range(5):
                context['ap']['highest_client_count_aps'].append(r['json_response']['queryResponse']['entity'][i]['accessPointsDTO'])

        #rogue APs
        context['ap']['rogues'] = list()
        r = api_request(
            'https://140.221.243.254/webacs/api/v1/data/Alarms.json?category.value="Rogue AP"&condition.value="UNCLASSIFIED_ROGUE_AP_DETECTED"&severity=ne("CLEARED")')
        if r.get('json_response'):
            context['ap']['rogues_count'] = r['json_response']['queryResponse']['@count']
        return context


class ApiCallView(LoginRequiredMixin, TemplateView):
    template_name = 'main/api_call.html'

    def get_context_data(self, **kwargs):
        context = super(ApiCallView, self).get_context_data(**kwargs)
        if self.request.GET.get('url'):
            context['request_url'] = self.request.GET.get('url')
        elif self.request.GET.get('query'):
            context['request_url'] = 'https://140.221.243.254/webacs/api/v1/%s.json' % self.request.GET['query']
            if self.request.GET.get('params'):
                context['request_url'] += self.request.GET.get('params')
        if context.get('request_url'):
            r = requests.get(
                context['request_url'],
                verify=False,
                auth=(settings.API_USER, settings.API_PASSWORD))
            try:
                context['response'] = r.json()
            except ValueError:
                context['response'] = r.content
            pp = pprint.PrettyPrinter(indent=4)
            context['pprint_json'] = pp.pformat(context['response'])
        return context
