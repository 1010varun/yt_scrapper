from django.contrib import admin
from .models import Video

@admin.register(Video)
class BookAdmin(admin.ModelAdmin):
    list_filter = ('search_query',)
