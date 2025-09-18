from django.utils.timezone import now
import datetime
from .models import Post
def clean_old_posts(): #delete posts older than 90 days
    cutoff_date = now() - datetime.timedelta(days=90)
    old_posts = Post.objects.filter(created_at__lt=cutoff_date)
    count = old_posts.count()
    old_posts.delete()
    print(f'[cron] Deleted {count} old posts order than {cutoff_date}')

    
