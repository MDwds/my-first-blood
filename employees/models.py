from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class EmployeeManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("必须填写登录账号")
        extra_fields.setdefault("role", Employee.Role.EMPLOYEE)
        user = self.model(username=username.strip(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("role", Employee.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("full_name", "系统管理员")
        return self.create_user(username, password, **extra_fields)


class Employee(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = "employee", "员工"
        ADMIN = "admin", "管理员"

    class Department(models.TextChoices):
        TECH = "tech", "技术部"
        PRODUCT = "product", "产品部"
        DESIGN = "design", "设计部"
        MARKETING = "marketing", "市场部"
        SALES = "sales", "销售部"
        OPERATIONS = "operations", "运营部"
        FINANCE = "finance", "财务部"
        HR = "hr", "人力资源部"
        ADMIN = "admin", "行政部"
        OTHER = "other", "其他"

    username = models.CharField(
        "员工账号 / 工号",
        max_length=50,
        unique=True,
        help_text="用于登录，建议使用工号。",
    )
    full_name = models.CharField("姓名", max_length=50)
    role = models.CharField("角色", max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    phone = models.CharField("手机号码", max_length=20, blank=True)
    department = models.CharField(
        "所属部门", max_length=20, choices=Department.choices, blank=True
    )
    position = models.CharField("职位", max_length=80, blank=True)
    hire_date = models.DateField("入职日期", null=True, blank=True)
    address = models.CharField("联系地址", max_length=200, blank=True)
    emergency_contact = models.CharField("紧急联系人", max_length=50, blank=True)
    emergency_phone = models.CharField("紧急联系电话", max_length=20, blank=True)
    bio = models.TextField("个人简介", max_length=500, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = EmployeeManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = "员工"
        verbose_name_plural = "员工"
        ordering = ["username"]

    def save(self, *args, **kwargs):
        if self.role == self.Role.ADMIN:
            self.is_staff = True
        elif not self.is_superuser:
            self.is_staff = False
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        return self.full_name or self.username

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def profile_completion(self):
        fields = [
            self.full_name,
            self.phone,
            self.email,
            self.department,
            self.position,
            self.hire_date,
            self.address,
            self.emergency_contact,
            self.emergency_phone,
        ]
        completed = sum(bool(value) for value in fields)
        return round(completed / len(fields) * 100)

    def __str__(self):
        return f"{self.display_name}（{self.username}）"
