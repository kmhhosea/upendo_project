from django.contrib import admin
from .models import Profile, Need, Donation

# Register models to admin site for easy management
admin.site.register(Profile)
admin.site.register(Need)
admin.site.register(Donation)




