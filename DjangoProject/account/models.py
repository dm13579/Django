from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True)
    aboutme = models.TextField(blank=True)
    photo = models.ImageField(blank=True)
    sex = models.TextField(blank=True)
    birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)
