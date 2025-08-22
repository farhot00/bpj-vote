from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden


class RateLimitMixin:
    rate_limit_key = 'user_or_ip'       # Default rate limit key
    rate_limit_rate = '90/m'    # Default rate limit value
    rate_limit_method = 'ALL'   # Default HTTP method to limit
    rate_limit_block = True     # Block request by default

    @method_decorator(ratelimit(key=rate_limit_key, rate=rate_limit_rate, method=rate_limit_method, block=rate_limit_block))
    def dispatch(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return HttpResponseForbidden('Rate limit exceeded.')
        return super().dispatch(request, *args, **kwargs)




class LoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)