from datetime import datetime

from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import EmployeeForm, AttendanceForm, AddAttendanceForm
from .models import Employee, Attendance


def _parse_date(value: str | None):
    """
    Parse YYYY-MM-DD to a `date` object.
    Returns None if empty/invalid so callers can safely ignore filters.
    """
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def dashboard(request: HttpRequest) -> HttpResponse:
    from_date = _parse_date(request.GET.get("from"))
    to_date = _parse_date(request.GET.get("to"))

    attendance_qs = Attendance.objects.all()
    if from_date:
        attendance_qs = attendance_qs.filter(date__gte=from_date)
    if to_date:
        attendance_qs = attendance_qs.filter(date__lte=to_date)

    total_employees = Employee.objects.count()
    total_attendance = attendance_qs.count()
    total_present = attendance_qs.filter(status="present").count()
    total_absent = attendance_qs.filter(status="absent").count()

    # Employees by department for bar chart
    by_department = (
        Employee.objects.values("department")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    dept_labels = [d["department"] or "Other" for d in by_department]
    dept_counts = [d["count"] for d in by_department]

    # Present days per employee (respecting date filters)
    date_q = Q()
    if from_date:
        date_q &= Q(attendances__date__gte=from_date)
    if to_date:
        date_q &= Q(attendances__date__lte=to_date)

    present_rows = (
        Employee.objects.annotate(
            present_days=Count(
                "attendances",
                filter=Q(attendances__status="present") & date_q,
            )
        )
        .values("id", "employee_id", "full_name", "department", "present_days")
        .order_by("-present_days", "full_name")
    )

    context = {
        "total_employees": total_employees,
        "total_attendance": total_attendance,
        "from_date": from_date.isoformat() if from_date else "",
        "to_date": to_date.isoformat() if to_date else "",
        "dept_labels": dept_labels,
        "dept_counts": dept_counts,
        "total_present": total_present,
        "total_absent": total_absent,
        "present_rows": list(present_rows),
    }
    return render(request, "employees/dashboard.html", context)


def employee_list(request: HttpRequest) -> HttpResponse:
    employees = Employee.objects.all().order_by("full_name")
    q = request.GET.get("q", "").strip()
    if q:
        employees = employees.filter(
            Q(full_name__icontains=q)
            | Q(email__icontains=q)
            | Q(employee_id__icontains=q)
            | Q(department__icontains=q)
        )
    context = {"employees": employees, "search_query": q}
    return render(request, "employees/employee_list.html", context)


def employee_add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect("employees:employee_list")
            except IntegrityError:
                form.add_error(
                    None,
                    "Employee with this ID or email already exists.",
                )
    else:
        form = EmployeeForm()
    return render(request, "employees/employee_add.html", {"form": form})


def attendance_add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AddAttendanceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect("employees:attendance_add")
            except IntegrityError:
                form.add_error("date", "Attendance for this employee and date already exists.")
    else:
        form = AddAttendanceForm()
    return render(request, "employees/attendance_add.html", {"form": form})


@require_http_methods(["POST"])
def employee_delete(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    return redirect("employees:employee_list")


def employee_attendance(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    from_date = _parse_date(request.GET.get("from"))
    to_date = _parse_date(request.GET.get("to"))

    total_present_days_all_time = employee.attendances.filter(status="present").count()

    attendances = employee.attendances.all()
    if from_date:
        attendances = attendances.filter(date__gte=from_date)
    if to_date:
        attendances = attendances.filter(date__lte=to_date)

    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            try:
                # Force employee to this one even if tampered in form
                attendance = form.save(commit=False)
                attendance.employee = employee
                attendance.save()
                query = request.GET.urlencode()
                url = reverse("employees:employee_attendance", kwargs={"pk": employee.pk})
                if query:
                    url = f"{url}?{query}"
                return redirect(url)
            except IntegrityError:
                form.add_error("date", "Attendance for this date already exists.")
    else:
        form = AttendanceForm()

    context = {
        "employee": employee,
        "attendances": attendances,
        "form": form,
        "from_date": from_date.isoformat() if from_date else "",
        "to_date": to_date.isoformat() if to_date else "",
        "present_days": attendances.filter(status="present").count(),
        "total_present_days": total_present_days_all_time,
    }
    return render(request, "employees/attendance.html", context)


def api_employees(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        employees = list(
            Employee.objects.all().values("id", "employee_id", "full_name", "email", "department")
        )
        return JsonResponse({"employees": employees})

    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                employee = form.save()
                data = {
                    "id": employee.id,
                    "employee_id": employee.employee_id,
                    "full_name": employee.full_name,
                    "email": employee.email,
                    "department": employee.department,
                }
                return JsonResponse(data, status=201)
            except IntegrityError:
                return JsonResponse(
                    {"error": "Employee with this ID or email already exists."},
                    status=400,
                )
        return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


def api_employee_attendance(request: HttpRequest, pk: int) -> JsonResponse:
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "GET":
        from_date = _parse_date(request.GET.get("from"))
        to_date = _parse_date(request.GET.get("to"))
        records_qs = employee.attendances.all()
        if from_date:
            records_qs = records_qs.filter(date__gte=from_date)
        if to_date:
            records_qs = records_qs.filter(date__lte=to_date)
        records = list(
            records_qs.values("id", "date", "status", "created_at")
        )
        return JsonResponse(
            {
                "employee": {
                    "id": employee.id,
                    "employee_id": employee.employee_id,
                    "full_name": employee.full_name,
                },
                "attendance": records,
            }
        )

    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            try:
                attendance = form.save(commit=False)
                attendance.employee = employee
                attendance.save()
                data = {
                    "id": attendance.id,
                    "date": attendance.date,
                    "status": attendance.status,
                }
                return JsonResponse(data, status=201)
            except IntegrityError:
                return JsonResponse(
                    {"error": "Attendance for this date already exists."},
                    status=400,
                )
        return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)

