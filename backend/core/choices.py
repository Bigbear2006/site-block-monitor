from django.db import models


class Language(models.TextChoices):
    EN = 'en', 'English'
    RU = 'ru', 'Русский'
