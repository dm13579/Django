import django
django.setup()

from celery import task
from .models import Playlist
from .musicapi import getmp3con
import datetime

@task
def update_url():
    list = Playlist.objects.order_by("-create_date")
    for num in range(list.count()):
        geturl = getmp3con(int(list[num].music_id))[0]['url']
        print(geturl)
        Playlist.objects.filter(music_id=list[num].music_id).update(music_url=geturl)

