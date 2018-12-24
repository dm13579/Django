from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Playlist(models.Model):
    music_id = models.TextField(max_length=20, null=True)
    music_name = models.TextField(max_length=20, null=True)
    music_albumimg = models.TextField(blank=True)
    music_url = models.TextField(blank=True)
    create_people = models.ForeignKey(User, related_name="playlist_people", on_delete=models.CASCADE)
    create_date = models.TextField(blank=True)


class Commentsong(models.Model):
    music_id = models.TextField(max_length=20, null=True)
    commentator = models.CharField(max_length=90)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    like = models.TextField(default='0')

    class Meta:
        ordering = ('-created',)


class Commentsongsecond(models.Model):
    commentator = models.ForeignKey(Commentsong, related_name='comtaor', on_delete=models.CASCADE)
    huifupeople = models.CharField(max_length=90)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)


class Commentlikestates(models.Model):
    commentator = models.ForeignKey(Commentsong, related_name='Commentlike', on_delete=models.CASCADE)
    states = models.TextField(max_length=2)
    dianzanuser = models.TextField(max_length=90, default="")


class Creategedan(models.Model):
    create_user = models.ForeignKey(User, related_name='create_user', on_delete=models.CASCADE)
    gedanname = models.CharField(max_length=200)
    user_like = models.ManyToManyField(User, related_name="gedan_like", blank=True)
    created = models.DateTimeField(auto_now_add=True)


class Gedansong(models.Model):
    gedan = models.ForeignKey(Creategedan, related_name='gedansong', on_delete=models.CASCADE)
    music_id = models.TextField(max_length=20, null=True)
    music_name = models.TextField(max_length=20, null=True)
    music_albumimg = models.TextField(blank=True)
    music_artist = models.TextField(blank=True)
    music_artist_id = models.TextField(blank=True)
    music_album = models.TextField(blank=True)
    music_album_id = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)


class DynamicPost(models.Model):
    author = models.ForeignKey(User, related_name="dynamic", on_delete=models.CASCADE)
    body = models.TextField()
    user_like = models.ManyToManyField(User, related_name="dynamic_like", blank=True)
    likes = models.TextField(default='0')
    created = models.DateTimeField(auto_now_add=True)


class Guanzhu(models.Model):
    guangzhufor = models.ForeignKey(User, related_name="guanzhufor", on_delete=models.CASCADE)
    guangzhuto = models.ForeignKey(User, related_name="guanzhuto", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class Commentdynamic(models.Model):
    comment_dynamic = models.ForeignKey(DynamicPost, related_name="comment_dynamic", on_delete=models.CASCADE)
    commentator = models.ForeignKey(User, related_name="commentator_dynamic", on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

