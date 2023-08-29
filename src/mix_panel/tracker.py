import os

from django.conf import settings
from mixpanel import Mixpanel, Consumer


class EmptyMixPanelTracker:
    def track(self, *args, **kwargs):
        print('Mixpanel event not sent because settings.MIXPANEL = False')


class MixPanelTracker:

    def __init__(self):

        if not settings.MIXPANEL:
            self.__mp = EmptyMixPanelTracker()
            return

        if not os.getenv('MIXPANEL_TOKEN'):
            raise Exception('MIXPANEL_TOKEN is not set')

        self.__mp = Mixpanel(
            os.getenv('MIXPANEL_TOKEN'),
            consumer=Consumer(api_host="api-eu.mixpanel.com"),
        )

    def track(self, user, event_name, properties):
        self.__mp.track(user, event_name, properties)



