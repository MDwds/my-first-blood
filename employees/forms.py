from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Employee


class StyledFormMixin:
    def apply_styles(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-checkbox"
            elif isinstance(widget, forms.Textarea):
                widget.attrs["class"] = "form-textarea"
            else:
                widget.attrs["class"] = "form-input"


class EmployeeAuthenticationForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "员工账号"
        self.fields["username"].widget.attrs["placeholder"] = "请输入员工账号或工号"
        self.fields["password"].label = "登录密码"
        self.fields["password"].widget.attrs["placeholder"] = "请输入登录密码"
        self.apply_styles()

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.role != Employee.Role.EMPLOYEE:
            raise ValidationError("该账号不是员工账号，请从管理员入口登录。", code="invalid_role")


class AdminAuthenticationForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "管理员账号"
        self.fields["username"].widget.attrs["placeholder"] = "请输入管理员账号"
        self.fields["password"].label = "登录密码"
        self.fields["password"].widget.attrs["placeholder"] = "请输入管理员密码"
        self.apply_styles()

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.role != Employee.Role.ADMIN or not user.is_staff:
            raise ValidationError("该账号没有管理员权限，请使用员工入口登录。", code="invalid_role")


class EmployeeCreateForm(StyledFormMixin, UserCreationForm):
    class Meta:
        model = Employee
        fields = [
            "username",
            "full_name",
            "phone",
            "email",
            "department",
            "position",
            "hire_date",
            "is_active",
            "address",
            "emergency_contact",
            "emergency_phone",
            "bio",
        ]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "is_active": "账号启用",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "初始密码"
        self.fields["password2"].label = "确认初始密码"
        self.fields["password1"].widget.attrs["placeholder"] = "至少 8 位，建议包含字母和数字"
        self.fields["password2"].widget.attrs["placeholder"] = "再次输入初始密码"
        self.apply_styles()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Employee.Role.EMPLOYEE
        if commit:
            user.save()
        return user


class EmployeeUpdateForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label="重置密码",
        required=False,
        widget=forms.PasswordInput,
        help_text="留空则不修改当前密码。",
    )
    password2 = forms.CharField(
        label="确认新密码",
        required=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = Employee
        fields = [
            "username",
            "full_name",
            "phone",
            "email",
            "department",
            "position",
            "hire_date",
            "is_active",
            "address",
            "emergency_contact",
            "emergency_phone",
            "bio",
        ]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "is_active": "账号启用",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["placeholder"] = "不修改请留空"
        self.fields["password2"].widget.attrs["placeholder"] = "再次输入新密码"
        self.apply_styles()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 or password2:
            if password1 != password2:
                self.add_error("password2", "两次输入的密码不一致。")
            elif password1:
                validate_password(password1, self.instance)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        user.role = Employee.Role.EMPLOYEE
        if commit:
            user.save()
        return user


class SelfProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "phone",
            "email",
            "address",
            "emergency_contact",
            "emergency_phone",
            "bio",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "phone": "手机号码",
            "address": "联系地址",
            "emergency_contact": "紧急联系人",
            "emergency_phone": "紧急联系电话",
            "bio": "个人简介",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
