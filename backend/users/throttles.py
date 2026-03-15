from rest_framework.throttling import AnonRateThrottle


class EmailResendThrottle(AnonRateThrottle):
    # setting email resend throttle
    # to block spam
    scope = "resend_email"

    def get_cache_key(self, request, view):
        # sensitive to email
        # changing ip address will not work
        email = request.data.get("email")

        if email:
            return self.cache_format % {"scope": self.scope, "ident": email}

        return super().get_cache_key(request, view)
