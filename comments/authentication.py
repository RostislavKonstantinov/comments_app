from rest_framework.authentication import BaseAuthentication

from comments.utils import get_user_from_request


class UserRequestParamAuthentication(BaseAuthentication):

    def authenticate(self, request):
        """
        Set user from request data for insert user in reversion
        Only for test app
        """
        request.user = user = get_user_from_request(request, raise_errors=False)
        return user, None
