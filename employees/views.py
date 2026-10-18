from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    AdminAuthenticationForm,
    EmployeeAuthenticationForm,
    EmployeeCreateForm,
    EmployeeUpdateForm,
    SelfProfileForm,
)
from .models import Employee


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.role != required_role:
                messages.error(request, "你无权访问该页面。")
                fallback = (
                    "employees:admin_dashboard"
                    if request.user.role == Employee.Role.ADMIN
                    else "employees:employee_dashboard"
                )
                return redirect(fallback)
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


employee_required = role_required(Employee.Role.EMPLOYEE)
admin_required = role_required(Employee.Role.ADMIN)


class RoleLoginView(LoginView):
    role = None
    dashboard_name = "employees:home"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("employees:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f"欢迎回来，{form.get_user().display_name}。")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(self.dashboard_name)


class EmployeeLoginView(RoleLoginView):
    template_name = "registration/employee_login.html"
    authentication_form = EmployeeAuthenticationForm
    dashboard_name = "employees:employee_dashboard"


class AdminLoginView(RoleLoginView):
    template_name = "registration/admin_login.html"
    authentication_form = AdminAuthenticationForm
    dashboard_name = "employees:admin_dashboard"


@login_required
def home(request):
    if request.user.role == Employee.Role.ADMIN:
        return redirect("employees:admin_dashboard")
    return redirect("employees:employee_dashboard")


@employee_required
def employee_dashboard(request):
    return render(
        request,
        "employees/employee_dashboard.html",
        {"employee": request.user},
    )


@employee_required
def profile_edit(request):
    if request.method == "POST":
        form = SelfProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "个人资料已更新。")
            return redirect("employees:employee_dashboard")
    else:
        form = SelfProfileForm(instance=request.user)
    return render(request, "employees/profile_edit.html", {"form": form})


@admin_required
def admin_dashboard(request):
    base_queryset = Employee.objects.filter(role=Employee.Role.EMPLOYEE)
    employees = base_queryset

    query = request.GET.get("q", "").strip()
    department = request.GET.get("department", "").strip()
    status = request.GET.get("status", "").strip()

    if query:
        employees = employees.filter(
            Q(username__icontains=query)
            | Q(full_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
            | Q(position__icontains=query)
        )
    if department:
        employees = employees.filter(department=department)
    if status == "active":
        employees = employees.filter(is_active=True)
    elif status == "inactive":
        employees = employees.filter(is_active=False)

    paginator = Paginator(employees.order_by("username"), 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    recent_cutoff = timezone.now() - timedelta(days=30)
    context = {
        "page_obj": page_obj,
        "total_employees": base_queryset.count(),
        "active_employees": base_queryset.filter(is_active=True).count(),
        "department_count": base_queryset.exclude(department="")
        .values("department")
        .distinct()
        .count(),
        "new_employees": base_queryset.filter(created_at__gte=recent_cutoff).count(),
        "departments": Employee.Department.choices,
        "query": query,
        "selected_department": department,
        "selected_status": status,
    }
    return render(request, "employees/admin_dashboard.html", context)


@admin_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk, role=Employee.Role.EMPLOYEE)
    return render(request, "employees/employee_detail.html", {"employee": employee})


@admin_required
def employee_create(request):
    if request.method == "POST":
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f"员工“{employee.display_name}”已创建。")
            return redirect("employees:employee_detail", pk=employee.pk)
    else:
        form = EmployeeCreateForm()
    return render(
        request,
        "employees/employee_form.html",
        {"form": form, "page_title": "录入员工信息", "submit_label": "创建员工"},
    )


@admin_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk, role=Employee.Role.EMPLOYEE)
    if request.method == "POST":
        form = EmployeeUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f"员工“{employee.display_name}”的信息已更新。")
            return redirect("employees:employee_detail", pk=employee.pk)
    else:
        form = EmployeeUpdateForm(instance=employee)
    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "employee": employee,
            "page_title": "修改员工信息",
            "submit_label": "保存修改",
        },
    )


@admin_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk, role=Employee.Role.EMPLOYEE)
    if request.method == "POST":
        display_name = employee.display_name
        employee.delete()
        messages.success(request, f"员工“{display_name}”已删除。")
        return redirect("employees:admin_dashboard")
    return render(
        request,
        "employees/employee_confirm_delete.html",
        {"employee": employee},
    )

