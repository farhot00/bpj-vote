from django_ratelimit.decorators import ratelimit
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden

class GlobalRateLimitMiddleware(MiddlewareMixin):
    @ratelimit(key='user_or_ip', rate='90/m', method='ALL', block=True)
    def process_request(self, request):
        if getattr(request, 'limited', False):
            return HttpResponseForbidden('Rate limit exceeded.')
