from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class UserRoles:
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

        choices = [
            (USER, USER),
            (MODERATOR, MODERATOR),
            (ADMIN, ADMIN),
        ]

    role = models.CharField(max_length=9, choices=UserRoles.choices, default=UserRoles.USER)
    bio = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(max_length=9)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Subscription(models.Model):
    reader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    def follower(self):
        return self.reader.username

    def following(self):
        return self.author.username

    def __str__(self):
        return f' {self.reader} subscribed to  {self.author}'
