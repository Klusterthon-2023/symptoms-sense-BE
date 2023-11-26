# accounts.admin

from django.contrib import admin

from .models import ChatHistory

admin.site.empty_value_display = "-empty-"


class ChatAdmin(admin.ModelAdmin):
    date_hierarchy = "date_time_created"
    empty_value_display = "-empty-"
    readonly_fields = ('id', 'date_time_created', 'date_time_modified')
    list_display = ['chat_identifier', 'request', 'response']
    ordering = ['-date_time_created', 'helpful']
    list_filter = ['helpful', 'date_time_created', 'chat_identifier']
    search_fields = ['request', 'response']
    list_per_page = 50
    list_max_show_all = 200
    list_select_related = True
    save_on_top = True

# Register your models here.
admin.site.register(ChatHistory, ChatAdmin)