from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "employees"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.EmployeeLoginView.as_view(), name="employee_login"),
    path("admin-login/", views.AdminLoginView.as_view(), name="admin_login"),
    path(
        "logout/",
        LogoutView.as_view(next_page="employees:employee_login"),
        name="logout",
    ),
    path("profile/", views.employee_dashboard, name="employee_dashboard"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("manage/", views.admin_dashboard, name="admin_dashboard"),
    path("manage/employees/add/", views.employee_create, name="employee_create"),
    path("manage/employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path(
        "manage/employees/<int:pk>/edit/",
        views.employee_update,
        name="employee_update",
    ),
    path(
        "manage/employees/<int:pk>/delete/",
        views.employee_delete,
        name="employee_delete",
    ),
]
