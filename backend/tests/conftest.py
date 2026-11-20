import pytest
from datetime import date, datetime, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.main import app
from app.models.profile import Profile
from app.models.schedule import Shift, EmployeeSchedule, ScheduleOverride, Holiday
from app.core.security import create_access_token

# Use StaticPool so all threads/sessions share the same in-memory SQLite database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed test admin & test employees
        admin = Profile(
            id="admin-uuid-1",
            employee_id="MB-ADMIN-01",
            full_name="Sir (Management)",
            email="management@mbsolarhub.com",
            designation="Executive Director",
            role="admin",
            joining_date=date(2024, 1, 1),
            is_active=True
        )
        emp1 = Profile(
            id="emp1-uuid-1",
            employee_id="MB-001",
            full_name="Rajesh Sharma",
            email="rajesh@mbsolarhub.com",
            designation="Business Analyst",
            role="employee",
            joining_date=date(2024, 2, 1),
            is_active=True
        )
        emp2 = Profile(
            id="emp2-uuid-2",
            employee_id="MB-002",
            full_name="Priya Patel",
            email="priya@mbsolarhub.com",
            designation="Software Engineer",
            role="employee",
            joining_date=date(2024, 3, 1),
            is_active=True
        )
        db.add_all([admin, emp1, emp2])
        db.commit()

        # Schedules:
        # Rajesh (emp1): Sunday off (6)
        # Priya (emp2): Wednesday off (2) - Works Sundays!
        sched1 = EmployeeSchedule(employee_id=emp1.id, weekly_off_day=6, effective_from=date(2024, 1, 1))
        sched2 = EmployeeSchedule(employee_id=emp2.id, weekly_off_day=2, effective_from=date(2024, 1, 1))
        db.add_all([sched1, sched2])
        db.commit()

        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token():
    return create_access_token({"sub": "admin-uuid-1", "email": "management@mbsolarhub.com", "role": "admin"})

@pytest.fixture
def emp1_token():
    return create_access_token({"sub": "emp1-uuid-1", "email": "rajesh@mbsolarhub.com", "role": "employee"})

@pytest.fixture
def emp2_token():
    return create_access_token({"sub": "emp2-uuid-2", "email": "priya@mbsolarhub.com", "role": "employee"})
