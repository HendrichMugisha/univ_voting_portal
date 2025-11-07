from django.contrib import admin
from .models import *

# Register all the app models right here 
admin.site.register(StudentProfile)

admin.site.register(Election)

admin.site.register(Position)

admin.site.register(Candidate)

admin.site.register(Vote)