from mix_panel import mp


class MixpanelMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.send_mixpanel_event(request)
        return response

    def send_mixpanel_event(self, request):
        username = request.user.username if request.user.is_authenticated else "Anonymous"
        view_name = request.resolver_match.view_name if request.resolver_match else "Unknown View"
        url_name = request.resolver_match.url_name if request.resolver_match else "Unknown URL"
        app_name = request.resolver_match.app_name if request.resolver_match else "Unknown App"

        try:
            mp.track(
                username,
                f'view_page',
                {
                    'view_name': view_name,
                    'url_name': url_name,
                    'app_name': app_name,
                }
            )
        except Exception as exc:
            print('Mixpanel Error: ', exc)
