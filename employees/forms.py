from django import forms

from .models import Employee, Attendance


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["employee_id", "full_name", "email", "department"]


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["date", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class AddAttendanceForm(forms.ModelForm):
    """Form for the dedicated Add Attendance page (includes employee choice)."""
    class Meta:
        model = Attendance
        fields = ["employee", "date", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "employee": forms.Select(attrs={"class": "form-select hrms-input", "id": "id_employee_select"}),
        }

