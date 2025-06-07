from django.contrib import admin
from django.contrib.auth.models import Group

from core import models

admin.site.unregister(Group)

admin.site.register(models.Site)
admin.site.register(models.Country)


class ClientMonitoredSiteInline(admin.TabularInline):
    model = models.ClientMonitoredSite
    can_delete = False


class SiteCheckInline(admin.TabularInline):
    model = models.SiteCheck
    can_delete = False


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    # inlines = [ClientMonitoredSiteInline]


@admin.register(models.MonitoredSite)
class MonitoredSiteAdmin(admin.ModelAdmin):
    list_select_related = ('site', 'country')
    # inlines = [SiteCheckInline]


@admin.register(models.ClientMonitoredSite)
class ClientMonitoredSiteAdmin(admin.ModelAdmin):
    list_select_related = (
        'client',
        'monitored_site__site',
        'monitored_site__country',
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(models.SiteCheck)
class SiteCheckAdmin(admin.ModelAdmin):
    list_select_related = ('monitored_site__site', 'monitored_site__country')
