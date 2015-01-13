from django.contrib import admin
from autosaloons.models import Autosaloon, City, AutosaloonBranch, BranchHall, DinnerWagon

admin.site.register(City)
admin.site.register(Autosaloon)
admin.site.register(AutosaloonBranch)
admin.site.register(BranchHall)
admin.site.register(DinnerWagon)
