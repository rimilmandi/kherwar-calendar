from django.contrib import admin
from .models import LunarMonth,NewMoon,HistoricalDate,LunarEvent,SolarEvent,Advertisement,SiteSetting
for model in [LunarMonth,NewMoon,HistoricalDate,LunarEvent,SolarEvent,Advertisement,SiteSetting]:
    admin.site.register(model)
