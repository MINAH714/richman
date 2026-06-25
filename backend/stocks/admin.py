from django.contrib import admin

# Register your models here.

from .models import Watchlist, Portfolio

admin.site.register(Watchlist)
admin.site.register(Portfolio)