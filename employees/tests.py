from django.test import TestCase
from django.urls import reverse

from .models import Employee


class EmployeePortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = Employee.objects.create_user(
            username="admin_test",
            password="Admin@123456",
            full_name="测试管理员",
            role=Employee.Role.ADMIN,
            is_staff=True,
        )
        cls.employee = Employee.objects.create_user(
            username="employee_test",
            password="Employee@123",
            full_name="测试员工",
            role=Employee.Role.EMPLOYEE,
            department=Employee.Department.TECH,
            position="开发工程师",
        )
        cls.colleague = Employee.objects.create_user(
            username="colleague_test",
            password="Employee@123",
            full_name="其他员工",
            role=Employee.Role.EMPLOYEE,
            department=Employee.Department.DESIGN,
        )

    def test_employee_can_login_and_open_own_profile(self):
        response = self.client.post(
            reverse("employees:employee_login"),
            {"username": "employee_test", "password": "Employee@123"},
        )
        self.assertRedirects(response, reverse("employees:employee_dashboard"))
        response = self.client.get(reverse("employees:employee_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "测试员工")
        self.assertNotContains(response, "colleague_test")

    def test_admin_is_rejected_from_employee_login(self):
        self.client.post(
            reverse("employees:employee_login"),
            {"username": "admin_test", "password": "Admin@123456"},
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_employee_cannot_access_admin_pages(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("employees:admin_dashboard"))
        self.assertRedirects(response, reverse("employees:employee_dashboard"))
        response = self.client.get(
            reverse("employees:employee_detail", args=[self.colleague.pk])
        )
        self.assertRedirects(response, reverse("employees:employee_dashboard"))

    def test_self_edit_ignores_protected_fields(self):
        self.client.force_login(self.employee)
        response = self.client.post(
            reverse("employees:profile_edit"),
            {
                "phone": "13900000000",
                "email": "employee@example.com",
                "address": "测试地址",
                "emergency_contact": "紧急联系人",
                "emergency_phone": "13900000001",
                "bio": "个人简介",
                "department": Employee.Department.FINANCE,
                "position": "被篡改的职位",
            },
        )
        self.assertRedirects(response, reverse("employees:employee_dashboard"))
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.phone, "13900000000")
        self.assertEqual(self.employee.department, Employee.Department.TECH)
        self.assertEqual(self.employee.position, "开发工程师")

    def test_admin_can_manage_employees(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("employees:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "测试员工")
        self.assertContains(response, "其他员工")

        response = self.client.post(
            reverse("employees:employee_create"),
            {
                "username": "new_employee",
                "full_name": "新员工",
                "phone": "13700000000",
                "email": "new@example.com",
                "department": Employee.Department.HR,
                "position": "招聘专员",
                "hire_date": "2026-10-17",
                "is_active": "on",
                "address": "",
                "emergency_contact": "",
                "emergency_phone": "",
                "bio": "",
                "password1": "StrongPass!2026#",
                "password2": "StrongPass!2026#",
            },
        )
        new_employee = Employee.objects.get(username="new_employee")
        self.assertRedirects(
            response, reverse("employees:employee_detail", args=[new_employee.pk])
        )

        response = self.client.post(
            reverse("employees:employee_update", args=[new_employee.pk]),
            {
                "username": "new_employee",
                "full_name": "新员工更新",
                "phone": "13700000001",
                "email": "new@example.com",
                "department": Employee.Department.HR,
                "position": "招聘主管",
                "hire_date": "2026-10-17",
                "is_active": "on",
                "address": "",
                "emergency_contact": "",
                "emergency_phone": "",
                "bio": "",
                "password1": "",
                "password2": "",
            },
        )
        self.assertRedirects(
            response, reverse("employees:employee_detail", args=[new_employee.pk])
        )
        new_employee.refresh_from_db()
        self.assertEqual(new_employee.full_name, "新员工更新")

        response = self.client.post(
            reverse("employees:employee_delete", args=[new_employee.pk])
        )
        self.assertRedirects(response, reverse("employees:admin_dashboard"))
        self.assertFalse(Employee.objects.filter(pk=new_employee.pk).exists())

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("employees:employee_dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('employees:employee_login')}?next={reverse('employees:employee_dashboard')}",
        )


