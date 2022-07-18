import tools
from datetime import datetime

# https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def project_is_offline():
    now = datetime.now()
    if now.isoweekday() == tools.constant.WEEK_DAY_MONDAY:
        return now.hour >= tools.constant.END_MONDAY_HOUR
    elif now.isoweekday() == tools.constant.WEEK_DAY_FRIDAY:
        return now.hour < tools.constant.START_FRIDAY_HOUR
    elif now.isoweekday() > tools.constant.WEEK_DAY_MONDAY:
        return True
    return now.isoweekday() < tools.constant.WEEK_DAY_FRIDAY


def user_has_rights(request):
    if project_is_offline():
        return False

    authorization = request.headers.get('Authorization', '')
    token = tools.security.get_token(authorization)
    data = tools.security.jwt_decode(token)
    if data is None:
        return False

    return True
