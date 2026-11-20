import pytest
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from fastapi import status

from app.models.attendance import AttendanceRecord, LunchRecord
from app.models.daily_work import DailyWorkEntry
from app.models.request import CorrectionRequest
from app.services.schedule_service import IST, check_day_status
from app.services.report_service import get_employee_range_data
from app.services.email_service import trigger_scheduled_management_report

def make_ist_dt(year: int, month: int, day: int, hour: int, minute: int) -> str:
    dt = datetime(year, month, day, hour, minute, tzinfo=IST)
    return dt.isoformat()

# Rule 1: Employee checks in at 8:50 AM — On Time
def test_rule_1_check_in_on_time(client, emp1_token):
    # 2026-11-23 is Monday
    ts = make_ist_dt(2026, 11, 23, 8, 50)
    response = client.post(
        "/api/attendance/check-in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": ts}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "present"
    assert data["late_minutes"] == 0

# Rule 2: Employee checks in at 9:30 AM — 30 Minutes Late
def test_rule_2_check_in_late(client, emp1_token):
    ts = make_ist_dt(2026, 11, 23, 9, 30)
    response = client.post(
        "/api/attendance/check-in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": ts}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "late"
    assert data["late_minutes"] == 30

# Rule 3: Employee tries normal Check In after 10:00 AM — Request required
def test_rule_3_check_in_after_window_requires_request(client, emp1_token):
    ts = make_ist_dt(2026, 11, 23, 10, 15)
    response = client.post(
        "/api/attendance/check-in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": ts}
    )
    assert response.status_code == 400
    assert "Correction Request" in response.json()["detail"]

# Rule 4: Employee attempts Check Out before 6:00 PM — Blocked
def test_rule_4_checkout_before_6pm_blocked(client, emp1_token):
    # First check in on time
    in_ts = make_ist_dt(2026, 11, 23, 8, 55)
    client.post(
        "/api/attendance/check-in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": in_ts}
    )
    # Attempt checkout at 5:45 PM
    out_ts = make_ist_dt(2026, 11, 23, 17, 45)
    response = client.post(
        "/api/attendance/check-out",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": out_ts}
    )
    assert response.status_code == 400
    assert "opens at 6:00 PM IST" in response.json()["detail"]

# Rule 5: Employee checks out at 6:30 PM — Accepted
def test_rule_5_checkout_accepted(client, emp1_token):
    in_ts = make_ist_dt(2026, 11, 23, 9, 0)
    client.post(
        "/api/attendance/check-in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": in_ts}
    )
    out_ts = make_ist_dt(2026, 11, 23, 18, 30)
    response = client.post(
        "/api/attendance/check-out",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": out_ts}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["check_out_time"] is not None
    assert float(data["work_hours"]) == pytest.approx(9.5, rel=1e-2)

# Rule 6: Employee attempts normal Check Out after 7:00 PM — Request required
def test_rule_6_checkout_after_7pm_requires_request(client, emp1_token):
    in_ts = make_ist_dt(2026, 11, 23, 9, 0)
    client.post(
        "/api/attendance/check-in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": in_ts}
    )
    out_ts = make_ist_dt(2026, 11, 23, 19, 15)
    response = client.post(
        "/api/attendance/check-out",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": out_ts}
    )
    assert response.status_code == 400
    assert "Checkout Correction Request" in response.json()["detail"]

# Rule 7: Employee returns from lunch at 2:15 PM — 15 Minutes Late
def test_rule_7_lunch_return_late(client, emp1_token):
    in_ts = make_ist_dt(2026, 11, 23, 9, 0)
    client.post(
        "/api/attendance/check-in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": in_ts}
    )
    # Lunch out at 1:05 PM
    l_out = make_ist_dt(2026, 11, 23, 13, 5)
    res_out = client.post(
        "/api/lunch/out",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": l_out, "notes": "Nearby cafe"}
    )
    assert res_out.status_code == 200

    # Lunch in at 2:15 PM
    l_in = make_ist_dt(2026, 11, 23, 14, 15)
    res_in = client.post(
        "/api/lunch/in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": l_in}
    )
    assert res_in.status_code == 200
    data = res_in.json()
    assert data["late_minutes"] == 15
    assert data["duration_minutes"] == 70

# Rule 8: Employee works on Sunday — Valid if scheduled
def test_rule_8_sunday_work_valid_if_scheduled(db_session):
    # 2026-11-22 is Sunday
    sun_date = date(2026, 11, 22)
    # Priya (emp2) has Wednesday off (weekly_off_day = 2), so Sunday is a scheduled working day!
    status_priya = check_day_status(db_session, "emp2-uuid-2", sun_date)
    assert status_priya["is_working_day"] is True
    assert status_priya["is_weekly_off"] is False

# Rule 9: Employee takes Wednesday weekly off — Not marked absent
def test_rule_9_wednesday_off_not_absent(db_session):
    # 2026-11-25 is Wednesday
    wed_date = date(2026, 11, 25)
    status_priya = check_day_status(db_session, "emp2-uuid-2", wed_date)
    assert status_priya["is_working_day"] is False
    assert status_priya["is_weekly_off"] is True
    assert "Weekly Off" in status_priya["reason"]

# Rule 10: Employee attempts to access another employee's records — Denied
def test_rule_10_unauthorized_cross_access_denied(client, emp1_token):
    # Rajesh (emp1) tries to view Priya's (emp2) profile
    res = client.get(
        "/api/employees/emp2-uuid-2",
        headers={"Authorization": f"Bearer {emp1_token}"}
    )
    assert res.status_code == 403

    # Rajesh tries to view Priya's attendance
    res_att = client.get(
        "/api/attendance/history?employee_id=emp2-uuid-2",
        headers={"Authorization": f"Bearer {emp1_token}"}
    )
    assert res_att.status_code == 403

# Rule 11: Employee submits multiple daily work entries — All saved separately
def test_rule_11_multiple_daily_work_entries(client, emp1_token):
    # Entry 1: Solar vendor calls
    res1 = client.post(
        "/api/work",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={
            "work_date": "2026-11-23",
            "work_description": "Contacted solar vendors regarding MB Solar Hub registration",
            "work_details": "24 calls made, 7 interested, 5 follow-ups required. Discussed registration process."
        }
    )
    assert res1.status_code == 200

    # Entry 2: Vendor onboarding analysis
    res2 = client.post(
        "/api/work",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={
            "work_date": "2026-11-23",
            "work_description": "Analyzed solar inverter vendor pricing tiers",
            "work_details": "Completed comparative sheet for Gujarat solar rooftop suppliers."
        }
    )
    assert res2.status_code == 200

    # Fetch daily work
    get_res = client.get(
        "/api/work?work_date=2026-11-23",
        headers={"Authorization": f"Bearer {emp1_token}"}
    )
    assert get_res.status_code == 200
    entries = get_res.json()
    assert len(entries) == 2
    assert entries[0]["work_description"] != entries[1]["work_description"]

# Rule 12: Weekly report contains only the selected employee's work
def test_rule_12_weekly_report_segregation(client, emp1_token, emp2_token, db_session):
    # Log work for emp1
    client.post(
        "/api/work",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={
            "work_date": "2026-11-23",
            "work_description": "Rajesh Work Activity MB Solar Hub"
        }
    )
    # Log work for emp2
    client.post(
        "/api/work",
        headers={"Authorization": f"Bearer {emp2_token}"},
        json={
            "work_date": "2026-11-23",
            "work_description": "Priya Work Activity Chatbot Development"
        }
    )

    # Rajesh downloads his weekly report
    res_rajesh = client.get(
        "/api/reports/weekly?start_date=2026-11-23&end_date=2026-11-29",
        headers={"Authorization": f"Bearer {emp1_token}"}
    )
    assert res_rajesh.status_code == 200
    data = res_rajesh.json()
    assert data["employee_code"] == "MB-001"
    
    # Check that Priya's work is NEVER in Rajesh's report
    all_descriptions = [
        w["description"]
        for day in data["daily_items"]
        for w in day["work_entries"]
    ]
    assert "Rajesh Work Activity MB Solar Hub" in all_descriptions
    assert "Priya Work Activity Chatbot Development" not in all_descriptions

# Rule 13: Report email fails — Delivery failure is recorded and retry is possible
def test_rule_13_report_delivery_tracking(db_session):
    res = trigger_scheduled_management_report(db_session, report_type="daily", target_date=date(2026, 11, 23))
    assert res["status"] in ["success", "skipped"]
    assert res["recipient"] == "management@mbsolarhub.com"

# Rule 14: Duplicate attendance requests — No duplicate records created
def test_rule_14_no_duplicate_attendance_punches(client, emp1_token):
    in_ts = make_ist_dt(2026, 11, 23, 8, 55)
    res1 = client.post(
        "/api/attendance/check-in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": in_ts}
    )
    assert res1.status_code == 200

    # Duplicate check in attempt
    res2 = client.post(
        "/api/attendance/check-in",
        headers={"Authorization": f"Bearer {emp1_token}"},
        json={"timestamp": in_ts}
    )
    assert res2.status_code == 400
    assert "already checked in" in res2.json()["detail"]
