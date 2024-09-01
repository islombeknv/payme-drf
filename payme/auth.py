import base64
import binascii

from django.contrib.auth import get_user_model, authenticate
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authentication import get_authorization_header


def authentication(request):
    auth = get_authorization_header(request).split()

    if len(auth) != 2 or auth[0].lower() != b"basic":
        return False

    try:
        auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(":")
    except (TypeError, UnicodeDecodeError, binascii.Error):
        return False

    userid, password = auth_parts[0], auth_parts[2]
    return authenticate_credentials(userid, password, request)


def authenticate_credentials(userid, password, request=None):
    credentials = {get_user_model().USERNAME_FIELD: userid, "password": password}
    user = authenticate(request=request, **credentials)

    return bool(user and user.is_active)
