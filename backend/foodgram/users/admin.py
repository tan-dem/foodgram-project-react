from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id", "username", "first_name", "last_name",
        "email", "password", "is_superuser",
    )
    list_editable = ("password",)
    search_fields = ("username", "first_name", "last_name",)
    list_filter = ("email", "username")
    empty_value_display = "-empty-"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
