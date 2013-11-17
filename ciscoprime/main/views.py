from django.views.generic import TemplateView
from django.conf import settings

from braces.views import LoginRequiredMixin
import requests
import pprint
import re

from .utils import api_request, analyze_rogue_alert_msg


class RogueDetailView(TemplateView):
    template_name = 'main/rogue_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RogueDetailView, self).get_context_data(**kwargs)

        #rogue APs
        context['rogues'] = list()
        context['events'] = list()
        r = api_request(
            'https://140.221.243.254/webacs/api/v1/data/Events.json?.full=true&correlated="%d"&severity=ne("CLEARED")' % int(self.kwargs.get('correlated', 0)))
        if r.get('json_response'):
            for entity in r['json_response']['queryResponse']['entity']:
                try:
                    event = analyze_rogue_alert_msg(entity['eventsDTO']['description'])
                    event.update(
                        {'id': entity['eventsDTO']['@id'],
                        'time': entity['eventsDTO']['eventFoundAt']}
                    )
                    context['events'].append(event)
                except ValueError:
                    #FIXME
                    print 'Non decodable rogue message "%s".'
        return context


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
            for entity in r['json_response']['queryResponse']['entity']:
                try:
                    rogue = analyze_rogue_alert_msg(entity['alarmsDTO']['message'])
                    rogue.update(
                        {'id': entity['alarmsDTO']['@id']}
                    )
                    rogues.append(rogue)
                except ValueError:
                    #FIXME
                    print 'Non decodable rogue message "%s".'
            a = []
            context['counts'] = dict()
            for r in rogues:
                if not r['ssid']:
                    r['ssid'] = 'hidden'
                if not r['ssid'] in a or not self.request.GET.get('simpleview'):
                    context['rogues'].append(r)
                    a.append(r['ssid'])
                if not context['counts'].get(r['ssid']):
                    context['counts'][r['ssid']] = 1
                else:
                    context['counts'][r['ssid']] = context['counts'].get(r['ssid']) + 1
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
