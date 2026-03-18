from django.urls import path

from . import views

app_name = "employees"

urlpatterns = [
    path("", views.employee_list, name="employee_list"),
    path("add/", views.employee_add, name="employee_add"),
    path("<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    path("<int:pk>/attendance/", views.employee_attendance, name="employee_attendance"),
    path("attendance/add/", views.attendance_add, name="attendance_add"),
    # JSON APIs
    path("api/employees/", views.api_employees, name="api_employees"),
    path("api/employees/<int:pk>/attendance/", views.api_employee_attendance, name="api_employee_attendance"),
]

