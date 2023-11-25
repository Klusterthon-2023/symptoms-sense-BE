# accounts.admin

from django.contrib import admin

from .models import ChatHistory

admin.site.empty_value_display = "-empty-"


class ChatAdmin(admin.ModelAdmin):
    date_hierarchy = "date_time_created"
    empty_value_display = "-empty-"
    readonly_fields = ('id', 'date_time_created', 'date_time_modified')
    list_display = ['user', 'request', 'request_audio', 'response']
    ordering = ['-date_time_created', 'user', 'helpful']
    list_filter = ['helpful', 'user', 'date_time_created']
    search_fields = ['request', 'response']
    list_per_page = 50
    list_max_show_all = 200
    list_select_related = True
    save_on_top = True

# Register your models here.
admin.site.register(ChatHistory, ChatAdmin)