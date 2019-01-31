from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


def get_user_from_request(request, raise_errors=True):
    """
    Get user object from request
    :param request: request object
    :param raise_errors: raise errors if user not found
    :return: User object
    """
    user_request_key = 'auth_user'
    user_id = request.data.get(user_request_key)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        if raise_errors:
            raise ValidationError({user_request_key: ["User does not exists"]})
        else:
            return None
    return user
