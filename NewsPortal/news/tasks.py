import datetime
from django.conf import settings
from django.utils import timezone
from news.models import Category, Post, PostCategory
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from celery import shared_task



@shared_task
def weekly_send_email_task():
    today = timezone.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(time_in_post__gte=last_week)
    categories = set(posts.values_list('categories__name', flat=True))
    subscribers = set(Category.objects.filter(name__in=categories).values_list('subscribers__email', flat=True))

    html_content = render_to_string(
        'daily_post.html',
        {
            # 'link': settings.SITE_URL,
            'link': f'{settings.SITE_URL}/news/',
            'posts': posts,
        }
    )

    msg = EmailMultiAlternatives(
        subject='Статьи за неделю(runapscheduler.py)',
        body='',
        from_email='smax85@yandex.ru',
        # settings.EMAIL_HOST_USER_FULL,
        to=['maksimus114114@gmail.com', 'sel-max@mail.ru'],
        # subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()





@shared_task
def send_email_about_new_post(pk):
    post = Post.objects.get(pk=pk)
    categories = post.categories.all()
    title = post.title
    subscribers_emails = []


    for category in categories:
        subscribers_users = category.subscribers.all()
        for sub_user in subscribers_users:
            subscribers_emails.append(sub_user.email)

    html_content = render_to_string(
        'post_created_email.html',
        {
            'Text': post.title,
            'link': f'{settings.SITE_URL}/news/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()

