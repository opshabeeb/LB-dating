from django.contrib import admin
from .models import Customuser,PersonalInfo,AdditionalInfo, UserMedia
# Register your models here.
admin.site.register(Customuser)
admin.site.register(PersonalInfo)
admin.site.register(AdditionalInfo)
admin.site.register(UserMedia)