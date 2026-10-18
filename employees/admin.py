from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    list_display = (
        "username",
        "full_name",
        "role",
        "department",
        "position",
        "phone",
        "is_active",
    )
    list_filter = ("role", "department", "is_active", "is_staff")
    search_fields = ("username", "full_name", "phone", "email", "position")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "员工资料",
            {
                "fields": (
                    "full_name",
                    "role",
                    "phone",
                    "department",
                    "position",
                    "hire_date",
                    "address",
                    "emergency_contact",
                    "emergency_phone",
                    "bio",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "员工资料",
            {
                "fields": (
                    "full_name",
                    "role",
                    "phone",
                    "department",
                    "position",
                    "hire_date",
                )
            },
        ),
    )
