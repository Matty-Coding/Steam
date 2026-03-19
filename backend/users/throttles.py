from rest_framework.throttling import AnonRateThrottle


class RateEmailSendThrottling(AnonRateThrottle):
    """
    AnonRateThrottle with scope set to None

    Used for resend email and login endpoints

    Based on email address instead of ip address
    """

    scope = "resend_email"

    def get_cache_key(self, request, view):
        # sensitive to email
        # changing ip address will not work
        email = request.data.get("email")

        if email:
            return self.cache_format % {"scope": self.scope, "ident": email}

        return super().get_cache_key(request, view)


class LoginThrottling(AnonRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        # sensitive to email
        # changing ip address will not work
        email = request.data.get("email")

        if email:
            return self.cache_format % {"scope": self.scope, "ident": email}

        return super().get_cache_key(request, view)
