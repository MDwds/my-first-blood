from django.core.management.base import BaseCommand

from employees.models import Employee


class Command(BaseCommand):
    help = "创建演示管理员和员工账号"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="同时重置已存在演示账号的密码",
        )

    def handle(self, *args, **options):
        admin, admin_created = Employee.objects.get_or_create(
            username="admin",
            defaults={
                "full_name": "系统管理员",
                "role": Employee.Role.ADMIN,
                "department": Employee.Department.ADMIN,
                "position": "系统管理员",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if admin_created or options["reset_passwords"]:
            admin.set_password("Admin@123456")
            admin.save()

        demo_employees = [
            {
                "username": "e001",
                "full_name": "林晓",
                "department": Employee.Department.TECH,
                "position": "Python 开发工程师",
                "phone": "13800000001",
                "email": "linxiao@example.com",
            },
            {
                "username": "e002",
                "full_name": "陈悦",
                "department": Employee.Department.DESIGN,
                "position": "UI 设计师",
                "phone": "13800000002",
                "email": "chenyue@example.com",
            },
            {
                "username": "e003",
                "full_name": "周诚",
                "department": Employee.Department.SALES,
                "position": "客户经理",
                "phone": "13800000003",
                "email": "zhoucheng@example.com",
            },
        ]

        for data in demo_employees:
            defaults = {
                key: value
                for key, value in data.items()
                if key != "username"
            }
            defaults["role"] = Employee.Role.EMPLOYEE
            employee, created = Employee.objects.get_or_create(
                username=data["username"],
                defaults=defaults,
            )
            if created or options["reset_passwords"]:
                employee.set_password("Employee@123")
                employee.save()

        self.stdout.write(self.style.SUCCESS("演示账号已准备完成。"))
        self.stdout.write("管理员：admin / Admin@123456")
        self.stdout.write("员工：e001、e002、e003 / Employee@123")


