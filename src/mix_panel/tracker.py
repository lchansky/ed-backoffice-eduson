import os

from django.conf import settings
from mixpanel import Mixpanel, Consumer, MixpanelException


class EmptyMixPanelTracker:
    def track(self, *args, **kwargs):
        print('Mixpanel event not sent because settings.MIXPANEL = False. Data: ', args, kwargs)

    def people_set(self, *args, **kwargs):
        print('Mixpanel user data not set because settings.MIXPANEL = False. Data: ', args, kwargs)


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

    def track(self, user, event_name, properties, user_properties=None):
        try:
            self.__mp.track(user, event_name, properties)
            if user_properties:
                self.set_user_properties(user, user_properties)
        except MixpanelException as exc:
            print('Error. Mixpanel event not sent. Data: ', user, event_name, properties)
            print(exc)

    def set_user_properties(self, user, user_properties):
        try:
            self.__mp.people_set(user, user_properties)
        except MixpanelException as exc:
            print('Error. Mixpanel user data not set. Data: ', user, user_properties)
            print(exc)



