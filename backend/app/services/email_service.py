import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.profile import Profile, AppSettings
from app.models.report import ReportHistory, ReportDeliveryLog
from app.services.report_service import (
    get_employee_range_data,
    generate_weekly_excel_report,
    generate_pdf_report,
    get_employee_daily_data
)
from app.services.schedule_service import get_now_ist, IST

def get_sir_email_recipient(db: Session) -> str:
    """Reads configured recipient email from DB app_settings or falls back to env settings.SIR_EMAIL"""
    setting = db.query(AppSettings).filter(AppSettings.key == "sir_email").first()
    if setting and setting.value:
        if isinstance(setting.value, dict) and "email" in setting.value:
            return setting.value["email"]
        elif isinstance(setting.value, str):
            return setting.value
    return settings.SIR_EMAIL

def send_email_with_attachments(
    recipient_email: str,
    subject: str,
    body_html: str,
    attachments: Optional[List[Dict[str, Any]]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Sends email via configured SMTP server. If credentials are not set,
    logs the delivery cleanly and succeeds in mock mode without failing server tasks.
    """
    from typing import Tuple
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        # Development / Mock mode
        print(f"[MOCK EMAIL SERVICE] To: {recipient_email} | Subject: {subject}")
        return True, None

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.EMAILS_FROM
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html"))

        if attachments:
            for att in attachments:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(att["content"])
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={att['filename']}")
                msg.attach(part)

        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, None
    except Exception as e:
        print(f"[EMAIL ERROR] Failed sending to {recipient_email}: {e}")
        return False, str(e)

def trigger_scheduled_management_report(db: Session, report_type: str = "daily", target_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Builds and dispatches the management summary report for Sir.
    Guards against duplicate deliveries on the same period and records history & delivery logs.
    """
    now = get_now_ist()
    target = target_date or (now.date())

    recipient = get_sir_email_recipient(db)

    if report_type == "daily":
        start_date = target
        end_date = target
        subject = f"[MB Solar Hub] Daily Attendance & Work Summary — {target.strftime('%d-%b-%Y')}"
    elif report_type == "weekly":
        # Previous Monday to Sunday
        start_date = target - timedelta(days=7)
        end_date = target - timedelta(days=1)
        subject = f"[MB Solar Hub] Weekly Operations Report ({start_date.strftime('%d-%b')} to {end_date.strftime('%d-%b-%Y')})"
    else: # monthly
        # First day of previous month to last day of previous month
        first_current = target.replace(day=1)
        end_date = first_current - timedelta(days=1)
        start_date = end_date.replace(day=1)
        subject = f"[MB Solar Hub] Monthly Operations Report ({start_date.strftime('%B %Y')})"

    # Check for existing completed delivery to prevent duplicate sends
    existing_history = db.query(ReportHistory).filter(
        ReportHistory.report_type == report_type,
        ReportHistory.period_start == start_date,
        ReportHistory.period_end == end_date,
        ReportHistory.employee_id.is_(None)
    ).first()

    if existing_history:
        success_log = db.query(ReportDeliveryLog).filter(
            ReportDeliveryLog.report_history_id == existing_history.id,
            ReportDeliveryLog.status == "sent"
        ).first()
        if success_log:
            return {"status": "skipped", "message": f"{report_type} report already delivered on {success_log.sent_at}"}

    # Gather data for all active employees
    employees = db.query(Profile).filter(Profile.is_active == True).order_by(Profile.full_name).all()

    summary_rows = []
    has_unresolved_corrections = False
    attachments = []

    for emp in employees:
        emp_data = get_employee_range_data(db, emp, start_date, end_date)
        if emp_data["has_unresolved_corrections"]:
            has_unresolved_corrections = True

        summary_rows.append(emp_data)

        # Generate individual employee weekly Excel if weekly or daily
        excel_io = generate_weekly_excel_report(db, emp, start_date, end_date)
        attachments.append({
            "filename": f"Report_{emp.employee_id}_{start_date.strftime('%Y%m%d')}.xlsx",
            "content": excel_io.getvalue()
        })

    # Record history
    history = ReportHistory(
        report_type=report_type,
        period_start=start_date,
        period_end=end_date,
        employee_id=None,
        file_format="xlsx",
        status="generated",
        has_unresolved_corrections=has_unresolved_corrections
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    # Compose HTML
    rows_html = ""
    for r in summary_rows:
        rows_html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #e2e8f0;"><b>{r['employee_name']}</b> ({r['employee_code']})</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{r['designation']}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0; text-align: center;">{r['scheduled_working_days']}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0; text-align: center; color: green;"><b>{r['present_days']}</b></td>
            <td style="padding: 8px; border: 1px solid #e2e8f0; text-align: center; color: orange;">{r['late_days']}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0; text-align: center;">{r['weekly_off_days']}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0; text-align: center;">{r['total_work_hours']} hrs</td>
        </tr>
        """

    notice_html = ""
    if has_unresolved_corrections:
        notice_html = """
        <div style="background-color: #fef2f2; border: 1px solid #f87171; color: #991b1b; padding: 12px; border-radius: 6px; margin-bottom: 16px;">
            ⚠️ <b>Attention:</b> Some employees have pending attendance or punch correction requests that are not yet approved.
        </div>
        """

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; color: #1e293b;">
        <div style="background-color: #0f172a; padding: 16px; border-radius: 8px 8px 0 0; text-align: center; color: #f8fafc;">
            <h2 style="margin: 0; color: #f59e0b;">MB SOLAR HUB</h2>
            <p style="margin: 4px 0 0; font-size: 14px;">{report_type.upper()} ATTENDANCE & WORK MANAGEMENT DIGEST</p>
        </div>
        <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none; background: #ffffff;">
            <p>Dear Management,</p>
            <p>Here is the scheduled {report_type} operations digest for the period <b>{start_date.strftime('%d-%b-%Y')}</b> to <b>{end_date.strftime('%d-%b-%Y')}</b>.</p>
            {notice_html}
            <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin: 16px 0;">
                <thead>
                    <tr style="background-color: #f1f5f9; text-align: left;">
                        <th style="padding: 8px; border: 1px solid #cbd5e1;">Employee</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1;">Designation</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">Scheduled</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">Present</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">Late</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">Offs</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">Hours</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <p style="font-size: 12px; color: #64748b;">Attached are the separate, individual weekly Excel spreadsheets for each employee, ready for records or review.</p>
        </div>
    </div>
    """

    success, err = send_email_with_attachments(recipient, subject, html, attachments)

    delivery = ReportDeliveryLog(
        report_history_id=history.id,
        recipient_email=recipient,
        recipient_name=settings.SIR_NAME,
        status="sent" if success else "failed",
        attempts=1,
        last_error=err,
        sent_at=datetime.utcnow() if success else None
    )
    db.add(delivery)
    db.commit()

    return {
        "status": "success" if success else "failed",
        "recipient": recipient,
        "report_history_id": history.id,
        "error": err
    }
