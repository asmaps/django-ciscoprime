from django.views.generic import TemplateView, ListView, CreateView
from django.conf import settings
from django.db.models import Max
from django.shortcuts import get_object_or_404

from braces.views import LoginRequiredMixin
import requests
import pprint
import re
import datetime

from .models import ClientCount, DisabledClient, RogueAP, TrackedRogue
from .utils import api_request, analyze_rogue_alert_msg, best_rssi_for_correlated


class FoundRogueView(LoginRequiredMixin, CreateView):
    template_name = 'main/found_rogue.html'
    model = TrackedRogue

    def get_rogue(self):
        return get_object_or_404(RogueAP, pk=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        self.rogue = self.get_rogue()
        return super(FoundRogueView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.rogue = self.get_rogue()
        return super(FoundRogueView, self).post(request, *args, **kwargs)

    def get_initial(self):
        return {
            'ap': self.rogue,
            'created_by': self.request.user,
        }

    def get_context_data(self, **kwargs):
        context = super(FoundRogueView, self).get_context_data(**kwargs)
        context['rogue'] = self.rogue
        return context


class DisabledClientsView(ListView):
    model = DisabledClient
    template_name = 'main/disabled_clients.html'


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
                        'time': entity['eventsDTO']['timeStamp']}
                    )
                    context['events'].append(event)
                except ValueError:
                    #FIXME
                    print 'Non decodable rogue message "%s".'
        #add alarm
        r = api_request(
            'https://140.221.243.254/webacs/api/v1/data/Alarms/%d.json?category.value="Rogue AP"&condition.value="UNCLASSIFIED_ROGUE_AP_DETECTED"&severity=ne("CLEARED")&.full=true' % int(self.kwargs.get('correlated', 0)))
        if r.get('json_response'):
            entity = r['json_response']['queryResponse']['entity'][0]
            try:
                rogue = analyze_rogue_alert_msg(entity['alarmsDTO']['message'])
                rogue.update(
                    {'id': entity['alarmsDTO']['@id'],
                    'time': entity['alarmsDTO']['timeStamp']}
                )
                context['events'].append(rogue)
                (context['rogue'], created) = RogueAP.objects.get_or_create(ssid=rogue['ssid'], mac=rogue['mac'], defaults={'correlated': entity['alarmsDTO']['@id']})
                context['rogue'].correlated = entity['alarmsDTO']['@id']
                context['rogue'].save()
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
                    rogue = None
                    if self.request.GET.get('showbest'):
                        rogue = best_rssi_for_correlated(int(entity['alarmsDTO']['@id']))
                    if not rogue:
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
            context['clients']['count'] = int(context['clients']['response']['json_response']['queryResponse']['@count'])
            
            #save client counts on our own because cisco api's ClientCounts output is 0
            if ClientCount.objects.all().count() == 0:
                cc = ClientCount.objects.create(count=context['clients']['count'])
                context['clients']['max_count_24'] = cc
                context['clients']['max_count_overall'] = cc
            elif not ClientCount.objects.all().order_by('-created')[0].count == context['clients']['count']:
                ClientCount.objects.create(count=context['clients']['count'])
            context['clients']['max_count_24'] = ClientCount.objects.filter(
                    created__gt=(datetime.datetime.now() - datetime.timedelta(hours=24))
                ).order_by('-count')[0]
            context['clients']['max_count_overall'] = ClientCount.objects.all().order_by('-count')[0]

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
