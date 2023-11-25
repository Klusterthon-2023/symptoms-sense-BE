# accounts.admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import UsersAuth

admin.site.empty_value_display = "-empty-"


class UsersAuthAdmin(UserAdmin):
    date_hierarchy = "date_time_created"
    empty_value_display = "-empty-"
    readonly_fields = ('id', 'last_login', 'date_time_created', 'date_time_modified', 'password')
    list_display = ['first_name', 'last_name', 'email', 'is_staff', 'is_deleted']
    ordering = ['-date_time_created', 'email',]
    list_filter = ['is_staff', 'is_deleted', 'date_time_created']
    search_fields = ['email', 'first_name', 'last_name', 'id']
    list_per_page = 50
    list_max_show_all = 200
    list_select_related = True
    save_on_top = True
    # inlines = [UserPasswordChangeInline]



# Register your models here.
admin.site.register(UsersAuth, UsersAuthAdmin)