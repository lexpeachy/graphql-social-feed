import datetime
from django.utils.timezone import now
from .models import User
def deactivate_inactive_users(): # deactivate user who have not logged in for the past 6 months
    cutoff_date = now() - datetime.timedelta(days=180)
    inactive_users = User.object.filter(is_active=True, last_login__lt=cutoff_date)
    count = inactive_users.count()
    inactive_users.update(is_active=False)
    print (f'[corn] Deactivated {count} inactive users (last login before {cutoff_date}).')

    