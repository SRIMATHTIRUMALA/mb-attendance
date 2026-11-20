import io
import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.models.profile import Profile
from app.models.attendance import AttendanceRecord, LunchRecord
from app.models.daily_work import DailyWorkEntry
from app.models.request import CorrectionRequest, LeaveRequest
from app.services.schedule_service import check_day_status, calculate_working_days, IST

def format_time_ist(dt: Optional[datetime]) -> str:
    if not dt:
        return "--"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(IST)
    else:
        dt = dt.astimezone(IST)
    return dt.strftime("%I:%M %p")

def get_employee_daily_data(db: Session, employee: Profile, target_date: date) -> Dict[str, Any]:
    day_status = check_day_status(db, employee.id, target_date)
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee.id,
        AttendanceRecord.work_date == target_date
    ).first()

    # Lunch details
    lunch_out_str = "--"
    lunch_in_str = "--"
    lunch_late = 0
    lunch_missing_in = False
    if record and record.lunch_records:
        latest_lunch = record.lunch_records[-1]
        lunch_out_str = format_time_ist(latest_lunch.lunch_out_time)
        lunch_in_str = format_time_ist(latest_lunch.lunch_in_time)
        lunch_late = latest_lunch.late_minutes
        lunch_missing_in = latest_lunch.missing_lunch_in

    # Work activities
    works = db.query(DailyWorkEntry).filter(
        DailyWorkEntry.employee_id == employee.id,
        DailyWorkEntry.work_date == target_date
    ).order_by(DailyWorkEntry.created_at.asc()).all()

    work_list = []
    for w in works:
        work_list.append({
            "id": w.id,
            "description": w.work_description,
            "details": w.work_details or "",
            "start_time": w.start_time.strftime("%I:%M %p") if w.start_time else "",
            "end_time": w.end_time.strftime("%I:%M %p") if w.end_time else "",
            "is_submitted": w.is_submitted
        })

    # Unresolved correction
    unresolved = db.query(CorrectionRequest).filter(
        CorrectionRequest.employee_id == employee.id,
        CorrectionRequest.target_date == target_date,
        CorrectionRequest.status == "pending"
    ).first()

    # Determine status display
    status_label = "Absent"
    if day_status["is_holiday"]:
        status_label = f"Holiday ({day_status['holiday_name']})"
    elif day_status["is_weekly_off"]:
        status_label = "Weekly Off"
    elif record:
        status_label = record.status.capitalize()
    
    return {
        "employee_id": employee.id,
        "employee_code": employee.employee_id,
        "employee_name": employee.full_name,
        "designation": employee.designation,
        "date": target_date,
        "attendance_status": status_label,
        "check_in_time": format_time_ist(record.check_in_time) if record else "--",
        "check_out_time": format_time_ist(record.check_out_time) if record else "--",
        "late_minutes": record.late_minutes if record else 0,
        "work_hours": record.work_hours if record else Decimal("0.00"),
        "lunch_out_time": lunch_out_str,
        "lunch_in_time": lunch_in_str,
        "lunch_late_minutes": lunch_late,
        "lunch_missing_in": lunch_missing_in,
        "work_entries": work_list,
        "has_unresolved_correction": bool(unresolved),
        "unresolved_correction_notes": unresolved.reason if unresolved else None
    }

def get_employee_range_data(db: Session, employee: Profile, start_date: date, end_date: date) -> Dict[str, Any]:
    current = start_date
    daily_items = []
    total_hours = Decimal("0.00")
    present_days = 0
    late_days = 0
    weekly_off_days = 0
    leave_days = 0
    has_any_unresolved = False

    while current <= end_date:
        item = get_employee_daily_data(db, employee, current)
        daily_items.append(item)
        if "Present" in item["attendance_status"] or "Late" in item["attendance_status"]:
            present_days += 1
            if item["late_minutes"] > 0:
                late_days += 1
        elif "Weekly Off" in item["attendance_status"]:
            weekly_off_days += 1
        elif "Leave" in item["attendance_status"]:
            leave_days += 1

        if item["work_hours"]:
            total_hours += Decimal(str(item["work_hours"]))
        if item["has_unresolved_correction"]:
            has_any_unresolved = True

        current += timedelta(days=1)

    scheduled_working_days = calculate_working_days(db, employee.id, start_date, end_date)

    return {
        "employee_id": employee.id,
        "employee_code": employee.employee_id,
        "employee_name": employee.full_name,
        "designation": employee.designation,
        "start_date": start_date,
        "end_date": end_date,
        "scheduled_working_days": scheduled_working_days,
        "present_days": present_days,
        "late_days": late_days,
        "weekly_off_days": weekly_off_days,
        "approved_leave_days": leave_days,
        "total_work_hours": total_hours,
        "daily_items": daily_items,
        "has_unresolved_corrections": has_any_unresolved
    }

def generate_weekly_excel_report(db: Session, employee: Profile, start_date: date, end_date: date) -> io.BytesIO:
    """
    Generates single-employee Weekly Activity & Attendance Excel file.
    Tailored so the employee can download and share via WhatsApp as requested!
    """
    data = get_employee_range_data(db, employee, start_date, end_date)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Activity-{employee.employee_id}"

    # Styles
    title_font = Font(name="Calibri", size=15, bold=True, color="1E293B")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True, color="0F172A")
    regular_font = Font(name="Calibri", size=10, color="334155")
    warning_font = Font(name="Calibri", size=10, bold=True, color="B91C1C")

    solar_fill = PatternFill(start_color="D97706", end_color="D97706", fill_type="solid") # MB Solar Hub Amber
    navy_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    sub_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    warn_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # Header Banner
    ws.merge_cells("A1:H1")
    ws["A1"] = "MB SOLAR HUB — WEEKLY ATTENDANCE & WORK REPORT"
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # Meta Info
    ws["A3"] = "Employee Name:"
    ws["B3"] = employee.full_name
    ws["A4"] = "Employee ID:"
    ws["B4"] = employee.employee_id
    ws["A5"] = "Designation:"
    ws["B5"] = employee.designation

    ws["E3"] = "Week Range:"
    ws["F3"] = f"{start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')}"
    ws["E4"] = "Scheduled Work Days:"
    ws["F4"] = data["scheduled_working_days"]
    ws["E5"] = "Present Days / Late:"
    ws["F5"] = f"{data['present_days']} / {data['late_days']}"

    for r in range(3, 6):
        ws[f"A{r}"].font = bold_font
        ws[f"B{r}"].font = regular_font
        ws[f"E{r}"].font = bold_font
        ws[f"F{r}"].font = regular_font

    if data["has_unresolved_corrections"]:
        ws.merge_cells("A6:H6")
        ws["A6"] = "⚠️ ATTENTION: This report contains pending/unresolved attendance correction requests."
        ws["A6"].font = warning_font
        ws["A6"].fill = warn_fill
        ws["A6"].alignment = Alignment(horizontal="center")

    # Table Headers
    headers = [
        "Date", "Day", "Attendance Status", "In Time", "Out Time",
        "Late (Mins)", "Lunch Status", "Daily Work Activities (Description & Feedback)"
    ]
    start_row = 8
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = navy_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[start_row].height = 24

    current_row = start_row + 1
    for day_data in data["daily_items"]:
        d_val = day_data["date"]
        # Format activities
        activities = []
        for w in day_data["work_entries"]:
            act_text = f"• {w['description']}"
            if w.get("details"):
                act_text += f"\n  Details: {w['details']}"
            activities.append(act_text)
        act_display = "\n\n".join(activities) if activities else "No activity logged."

        lunch_display = f"Out: {day_data['lunch_out_time']} | In: {day_data['lunch_in_time']}"
        if day_data["lunch_late_minutes"] > 0:
            lunch_display += f" ({day_data['lunch_late_minutes']}m late return)"

        row_values = [
            d_val.strftime("%d-%b-%Y"),
            d_val.strftime("%A"),
            day_data["attendance_status"],
            day_data["check_in_time"],
            day_data["check_out_time"],
            day_data["late_minutes"] if day_data["late_minutes"] > 0 else "-",
            lunch_display,
            act_display
        ]

        for col_idx, val in enumerate(row_values, 1):
            cell = ws.cell(row=current_row, column=col_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            if col_idx in [1, 2, 3, 4, 5, 6]:
                cell.alignment = Alignment(horizontal="center", vertical="top")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            
            # Subtle highlight on weekly off or unresolved
            if "Weekly Off" in day_data["attendance_status"]:
                cell.fill = sub_fill
            if day_data["has_unresolved_correction"] and col_idx == 3:
                cell.fill = warn_fill

        ws.row_dimensions[current_row].height = max(30, 20 + len(activities) * 22)
        current_row += 1

    # Column dimensions
    ws.column_dimensions['A'].width = 14
    ws.column_dimensions['B'].width = 13
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 13
    ws.column_dimensions['G'].width = 28
    ws.column_dimensions['H'].width = 50

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def generate_pdf_report(db: Session, employee: Profile, start_date: date, end_date: date) -> io.BytesIO:
    """
    Generates a clean PDF Report for the employee using ReportLab.
    """
    data = get_employee_range_data(db, employee, start_date, end_date)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        alignment=1 # Center
    )

    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )

    story.append(Paragraph("<b>MB SOLAR HUB</b>", title_style))
    story.append(Paragraph("Employee Attendance & Daily Work Report", ParagraphStyle('SubHeader', parent=title_style, fontSize=12, textColor=colors.HexColor('#D97706'))))
    story.append(Spacer(1, 12))

    meta_text = f"""
    <b>Employee Name:</b> {employee.full_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>ID:</b> {employee.employee_id} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Designation:</b> {employee.designation}<br/>
    <b>Period:</b> {start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Scheduled Work Days:</b> {data['scheduled_working_days']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Present Days:</b> {data['present_days']}
    """
    story.append(Paragraph(meta_text, sub_style))
    story.append(Spacer(1, 10))

    if data["has_unresolved_corrections"]:
        warn_style = ParagraphStyle('Warn', parent=sub_style, textColor=colors.HexColor('#DC2626'), backColor=colors.HexColor('#FEE2E2'))
        story.append(Paragraph("⚠️ <b>Notice:</b> This report contains pending attendance corrections.", warn_style))
        story.append(Spacer(1, 10))

    # Table content
    table_data = [
        ["Date", "Status", "In Time", "Out Time", "Work Hours", "Work Activities"]
    ]

    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#1E293B'))

    for day in data["daily_items"]:
        act_lines = []
        for w in day["work_entries"]:
            txt = f"• {w['description']}"
            if w.get("details"):
                txt += f" <i>({w['details']})</i>"
            act_lines.append(txt)
        act_cell = "<br/>".join(act_lines) if act_lines else "--"

        table_data.append([
            day["date"].strftime("%d-%b (%a)"),
            day["attendance_status"],
            day["check_in_time"],
            day["check_out_time"],
            str(day["work_hours"]) if day["work_hours"] else "--",
            Paragraph(act_cell, cell_style)
        ])

    table = Table(table_data, colWidths=[65, 80, 55, 55, 60, 230])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))

    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer
