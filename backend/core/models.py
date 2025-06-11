from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

from bot.utils.formatters import date_to_str
from core.choices import Language
from core.managers import (
    ClientManager,
    ClientMonitoredSiteManager,
    MonitoredSiteManager,
    PaymentManager,
)


class User(AbstractUser):
    pass


class Client(models.Model):
    id = models.PositiveBigIntegerField('Telegram ID', primary_key=True)
    first_name = models.CharField('Имя', max_length=255)
    last_name = models.CharField(
        'Фамилия',
        max_length=255,
        null=True,
        blank=True,
    )
    username = models.CharField('Ник', max_length=32, null=True, blank=True)
    is_premium = models.BooleanField('Есть премиум', default=False)
    language = models.CharField(
        'Язык',
        max_length=10,
        choices=Language,
        default=Language.EN,
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    objects = ClientManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        username = self.first_name
        if self.username:
            username += f' (@{self.username})'
        return username

    def has_trial(self):
        return self.created_at < now() + timedelta(days=3)


class Site(models.Model):
    url = models.URLField('URL', unique=True)

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'
        ordering = ['url']

    def __str__(self):
        return self.url


class Country(models.Model):
    code = models.CharField(
        'Код',
        max_length=20,
        unique=True,
        primary_key=True,
    )
    name = models.CharField('Название', max_length=255)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'
        ordering = ['name']

    def __str__(self):
        return self.name


class MonitoredSite(models.Model):
    task_id = models.PositiveBigIntegerField(
        'ID Задачи в PingAdmin',
        primary_key=True,
    )
    site = models.ForeignKey(
        Site,
        models.RESTRICT,
        'monitored_sites',
        verbose_name='Сайт',
    )
    country = models.ForeignKey(
        Country,
        models.RESTRICT,
        'monitored_sites',
        verbose_name='Страна',
    )
    period = models.IntegerField('Периодичность проверки')
    last_checks: list['SiteCheck'] | None
    objects = MonitoredSiteManager()

    class Meta:
        unique_together = ('site', 'country')
        verbose_name = 'Отслеживаемый сайт'
        verbose_name_plural = 'Отслеживаемые сайты'

    def __str__(self):
        return f'{self.site} ({self.country})'


class ClientMonitoredSite(models.Model):
    client = models.ForeignKey(
        Client,
        models.RESTRICT,
        'monitored_sites',
        verbose_name='Пользователь',
    )
    monitored_site = models.ForeignKey(
        MonitoredSite,
        models.RESTRICT,
        'clients',
        verbose_name='Сайт',
    )
    is_active = models.BooleanField('Активен', default=True)
    subscription_end = models.DateTimeField('Оплачен до')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)
    objects = ClientMonitoredSiteManager()

    class Meta:
        unique_together = ('client', 'monitored_site')
        verbose_name = 'Отслеживаемый пользователем сайт'
        verbose_name_plural = 'Отслеживаемые пользователями сайты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client} - {self.monitored_site}'

    async def prolong_subscription(self, days: int = 30):
        subscription_end = self.subscription_end or now()
        self.subscription_end = subscription_end + timedelta(days=days)
        await self.asave()


class SiteCheck(models.Model):
    monitored_site = models.ForeignKey(
        MonitoredSite,
        models.CASCADE,
        'checks',
        verbose_name='Отслеживаемый сайт',
    )
    status = models.BooleanField('Статус')
    description = models.TextField('Описание', blank=True)
    country = models.ForeignKey(
        Country,
        models.CASCADE,
        'checks',
        verbose_name='Страна',
    )
    date = models.DateTimeField('Дата')

    class Meta:
        verbose_name = 'Проверка статуса'
        verbose_name_plural = 'Проверки статусов'
        ordering = ['-date']

    @property
    def status_str(self):
        return 'работает' if self.status else 'не работает'

    def __str__(self):
        return (
            f'[{date_to_str(self.date)}] '
            f'{self.monitored_site} - {self.status_str}'
        )


class Payment(models.Model):
    client = models.ForeignKey(
        Client,
        models.RESTRICT,
        'payments',
        verbose_name='Пользователь',
    )
    charge_id = models.CharField('ID платежа')
    payload = models.CharField('Тип оплаты')
    date = models.DateTimeField(auto_now_add=True)
    objects = PaymentManager()

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'
        ordering = ['-date']

    def __str__(self):
        return f'[{date_to_str(self.date)}] {self.client}'
