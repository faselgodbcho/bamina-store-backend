import datetime
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user, stay_logged_in):
    refresh = RefreshToken.for_user(user)

    if stay_logged_in:
        refresh.set_exp(lifetime=datetime.timedelta(days=7))
    else:
        refresh.set_exp(lifetime=datetime.timedelta(days=1))

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }
