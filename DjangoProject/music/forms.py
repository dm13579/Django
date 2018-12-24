from django import forms
from .models import Playlist, Commentsong, Creategedan, DynamicPost


class PlaylistForm(forms.ModelForm):

    class Meta:
        model = Playlist
        fields = ("music_id", "music_name", "music_albumimg", "music_url")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Commentsong
        fields = ('body',)


class DynamicForm(forms.ModelForm):
    class Meta:
        model = DynamicPost
        fields = ('body',)


class CreategedanForm(forms.ModelForm):
    class Meta:
        model = Creategedan
        fields = ('gedanname',)