from mix_panel import mp


class MixpanelMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.send_mixpanel_event(request)
        return response

    def send_mixpanel_event(self, request):
        if request.user.is_authenticated:
            username = request.user.username
            user_properties = {
                '$username': request.user.username,
                '$first_name': request.user.first_name,
                '$last_name': request.user.last_name,
                '$email': request.user.email,
            }
        else:
            username = "Anonymous"
            user_properties = {"$username": "Anonymous"}

        view_name = request.resolver_match.view_name if request.resolver_match else "Unknown View"
        url_name = request.resolver_match.url_name if request.resolver_match else "Unknown URL"
        if hasattr(request.resolver_match, 'func'):
            app_name = request.resolver_match.func.__module__.split('.')[0]
        else:
            app_name = 'Unknown App'

        if 'api' in url_name:
            return
        try:
            mp.track(
                username,
                f'view_page',
                {
                    'view_name': view_name,
                    'url_name': url_name,
                    'app_name': app_name,
                },
                user_properties=user_properties,
            )
        except Exception as exc:
            print('Mixpanel Error: ', exc)
