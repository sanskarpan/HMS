"""
Test script for verifying all database models and relationships.

Usage:
    pytest backend/test_models.py
    OR
    python backend/test_models.py
"""
import os
import sys
from datetime import date, time, timedelta

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.app.models import (
    db, User, Department, Doctor, DoctorAvailability,
    Patient, Appointment, Treatment
)


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture(scope='module')
def app():
    """Create application for the tests."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        # Seed basic data
        _seed_test_data()
        yield app
        db.session.remove()


@pytest.fixture(scope='module')
def app_context(app):
    """Provide application context for tests."""
    with app.app_context():
        yield


@pytest.fixture(scope='module')
def department(app_context):
    """Create a department for testing."""
    dept = Department.find_by_name('Cardiology')
    if not dept:
        dept = Department(
            name='Cardiology',
            description='Heart and cardiovascular care'
        )
        db.session.add(dept)
        db.session.commit()
    return dept


@pytest.fixture(scope='module')
def doctor_user(app_context):
    """Create a doctor user for testing."""
    user = User.find_by_username('dr_smith_test')
    if not user:
        user = User(
            username='dr_smith_test',
            email='dr.smith.test@hospital.com',
            password='doctor123',
            role='doctor'
        )
        db.session.add(user)
        db.session.commit()
    return user


@pytest.fixture(scope='module')
def patient_user(app_context):
    """Create a patient user for testing."""
    user = User.find_by_username('john_doe_test')
    if not user:
        user = User(
            username='john_doe_test',
            email='john.test@email.com',
            password='patient123',
            role='patient'
        )
        db.session.add(user)
        db.session.commit()
    return user


@pytest.fixture(scope='module')
def doctor(doctor_user, department):
    """Create a doctor profile for testing."""
    doc = Doctor.query.filter_by(user_id=doctor_user.id).first()
    if not doc:
        doc = Doctor(
            user_id=doctor_user.id,
            department_id=department.id,
            full_name='Dr. John Smith Test',
            qualification='MBBS, MD - Cardiology',
            experience_years=15,
            phone='+1234567890',
            bio='Experienced cardiologist.',
            consultation_fee=150.00
        )
        db.session.add(doc)
        db.session.commit()
    return doc


@pytest.fixture(scope='module')
def patient(patient_user):
    """Create a patient profile for testing."""
    pat = Patient.query.filter_by(user_id=patient_user.id).first()
    if not pat:
        pat = Patient(
            user_id=patient_user.id,
            full_name='John Doe Test',
            phone='+1987654321',
            date_of_birth=date(1990, 5, 15),
            gender='male',
            address='123 Main Street, City',
            blood_group='O+',
            medical_history='No known allergies'
        )
        db.session.add(pat)
        db.session.commit()
    return pat


@pytest.fixture(scope='module')
def appointment(doctor, patient):
    """Create an appointment for testing."""
    tomorrow = date.today() + timedelta(days=1)
    apt_time = time(9, 0)

    # Check if appointment already exists
    apt = Appointment.query.filter_by(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=tomorrow,
        appointment_time=apt_time
    ).first()

    if not apt:
        apt = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=doctor.department_id,
            appointment_date=tomorrow,
            appointment_time=apt_time,
            reason='Regular checkup'
        )
        db.session.add(apt)
        db.session.commit()
    return apt


def _seed_test_data():
    """Seed basic test data."""
    # Create admin if not exists
    admin = User.find_by_username('admin')
    if not admin:
        admin = User(
            username='admin',
            email='admin@hospital.com',
            password='admin123',
            role='admin'
        )
        db.session.add(admin)

    # Create departments if not exist
    departments_data = [
        ('Cardiology', 'Heart and cardiovascular care'),
        ('Neurology', 'Brain and nervous system'),
        ('Orthopedics', 'Bone and joint care'),
        ('Pediatrics', 'Child healthcare'),
        ('Dermatology', 'Skin care'),
        ('Ophthalmology', 'Eye care'),
        ('ENT', 'Ear, nose, and throat'),
        ('Psychiatry', 'Mental health'),
        ('Gastroenterology', 'Digestive system'),
        ('Pulmonology', 'Respiratory system'),
    ]

    for name, desc in departments_data:
        if not Department.find_by_name(name):
            dept = Department(name=name, description=desc)
            db.session.add(dept)

    db.session.commit()


# ============================================================================
# Test Functions
# ============================================================================

def test_user_model(app_context):
    """Test User model functionality."""
    # Test finding admin
    admin = User.find_by_username('admin')
    assert admin is not None, "Admin user not found"
    assert admin.is_admin, "Admin role not set correctly"

    # Test creating a new user
    test_user = User.find_by_username('test_user_unique')
    if not test_user:
        test_user = User(
            username='test_user_unique',
            email='test_unique@hospital.com',
            password='test123',
            role='patient'
        )
        db.session.add(test_user)
        db.session.commit()

    assert test_user.is_patient, "Patient role not set correctly"
    assert test_user.check_password('test123'), "Password check failed"

    # Test find by email
    found = User.find_by_email('test_unique@hospital.com')
    assert found is not None, "User not found by email"


def test_department_model(app_context):
    """Test Department model functionality."""
    # Test finding department
    cardiology = Department.find_by_name('Cardiology')
    assert cardiology is not None, "Cardiology department not found"

    # Test get all active
    departments = Department.get_all_active()
    assert len(departments) >= 1, "No departments found"

    # Test search
    results = Department.search('neuro')
    assert len(results) >= 1, "Search should find Neurology"


def test_doctor_model(doctor_user, department):
    """Test Doctor model functionality."""
    # Create doctor profile
    doctor = Doctor.query.filter_by(user_id=doctor_user.id).first()
    if not doctor:
        doctor = Doctor(
            user_id=doctor_user.id,
            department_id=department.id,
            full_name='Dr. John Smith',
            qualification='MBBS, MD - Cardiology',
            experience_years=15,
            phone='+1234567890',
            bio='Experienced cardiologist.',
            consultation_fee=150.00
        )
        db.session.add(doctor)
        db.session.commit()

    # Test relationships
    assert doctor.user == doctor_user, "User relationship not working"
    assert doctor.department == department, "Department relationship not working"
    assert doctor.email == doctor_user.email, "Email property not working"

    # Test to_dict
    doctor_dict = doctor.to_dict(include_department=True)
    assert 'department' in doctor_dict, "Department not in dict"


def test_availability_model(doctor):
    """Test DoctorAvailability model functionality."""
    tomorrow = date.today() + timedelta(days=1)

    # Set availability for tomorrow
    availability = DoctorAvailability.set_availability(
        doctor_id=doctor.id,
        availability_date=tomorrow,
        morning_start=time(8, 0),
        morning_end=time(12, 0),
        evening_start=time(16, 0),
        evening_end=time(21, 0),
        slot_duration=30
    )
    db.session.commit()

    # Test slot generation
    morning_slots = availability.morning_slots
    evening_slots = availability.evening_slots
    assert len(morning_slots) == 8, f"Expected 8 morning slots, got {len(morning_slots)}"
    assert len(evening_slots) == 10, f"Expected 10 evening slots, got {len(evening_slots)}"

    # Test to_dict
    avail_dict = availability.to_dict(include_slots=True)
    assert 'morning_slots' in avail_dict, "Slots not in dict"


def test_patient_model(patient_user):
    """Test Patient model functionality."""
    # Create patient profile
    patient = Patient.query.filter_by(user_id=patient_user.id).first()
    if not patient:
        patient = Patient(
            user_id=patient_user.id,
            full_name='John Doe',
            phone='+1987654321',
            date_of_birth=date(1990, 5, 15),
            gender='male',
            address='123 Main Street, City',
            blood_group='O+',
            medical_history='No known allergies'
        )
        db.session.add(patient)
        db.session.commit()

    # Test age calculation
    assert patient.age is not None, "Age calculation failed"

    # Test relationships
    assert patient.user == patient_user, "User relationship not working"
    assert patient.email == patient_user.email, "Email property not working"


def test_appointment_model(doctor, patient):
    """Test Appointment model functionality."""
    tomorrow = date.today() + timedelta(days=1)
    apt_time = time(10, 30)  # Different time to avoid conflict

    # Create appointment
    appointment = Appointment.query.filter_by(
        doctor_id=doctor.id,
        appointment_date=tomorrow,
        appointment_time=apt_time
    ).first()

    if not appointment:
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=doctor.department_id,
            appointment_date=tomorrow,
            appointment_time=apt_time,
            reason='Regular checkup'
        )
        db.session.add(appointment)
        db.session.commit()

    # Test relationships
    assert appointment.patient == patient, "Patient relationship not working"
    assert appointment.doctor == doctor, "Doctor relationship not working"

    # Test properties
    assert appointment.is_upcoming, "is_upcoming should be True"
    assert appointment.can_cancel, "can_cancel should be True"
    assert appointment.status == 'booked', "Status should be 'booked'"

    # Test slot availability
    is_available = Appointment.check_slot_available(doctor.id, tomorrow, apt_time)
    assert not is_available, "Slot should not be available"


def test_treatment_model(appointment):
    """Test Treatment model functionality."""
    # First complete the appointment if not already
    if appointment.status != 'completed':
        appointment.complete()
        db.session.commit()

    # Check if treatment exists
    treatment = Treatment.query.filter_by(appointment_id=appointment.id).first()
    if not treatment:
        treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis='Mild hypertension',
            prescription='Amlodipine 5mg\nAspirin 75mg',
            notes='Patient advised to reduce salt intake.',
            tests_recommended='ECG\nBlood pressure monitoring',
            follow_up_date=date.today() + timedelta(days=30),
            visit_type='in-person'
        )
        db.session.add(treatment)
        db.session.commit()

    # Test relationships
    assert treatment.appointment == appointment, "Appointment relationship not working"
    assert treatment.patient == appointment.patient, "Patient access not working"
    assert treatment.doctor == appointment.doctor, "Doctor access not working"

    # Test prescription list
    meds = treatment.get_prescription_list()
    assert len(meds) == 2, "Prescription parsing failed"

    # Test export dict
    export = treatment.to_export_dict()
    assert 'diagnosis' in export, "Export dict missing fields"


# ============================================================================
# Standalone Script Mode
# ============================================================================

def run_all_tests():
    """Run all model tests when executed as a script."""
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 50)
        print("Hospital Management System - Model Tests")
        print("=" * 50)

        try:
            # Seed test data
            _seed_test_data()

            # Run tests in order
            print("\n=== Testing User Model ===")
            test_user_model(None)  # app_context fixture not needed in script mode
            print("  User model tests passed!")

            print("\n=== Testing Department Model ===")
            test_department_model(None)
            print("  Department model tests passed!")

            # Get/create fixtures
            department = Department.find_by_name('Cardiology')

            doctor_user = User.find_by_username('dr_smith_test')
            if not doctor_user:
                doctor_user = User(
                    username='dr_smith_test',
                    email='dr.smith.test@hospital.com',
                    password='doctor123',
                    role='doctor'
                )
                db.session.add(doctor_user)
                db.session.commit()

            patient_user = User.find_by_username('john_doe_test')
            if not patient_user:
                patient_user = User(
                    username='john_doe_test',
                    email='john.test@email.com',
                    password='patient123',
                    role='patient'
                )
                db.session.add(patient_user)
                db.session.commit()

            print("\n=== Testing Doctor Model ===")
            test_doctor_model(doctor_user, department)
            print("  Doctor model tests passed!")

            doctor = Doctor.query.filter_by(user_id=doctor_user.id).first()

            print("\n=== Testing Availability Model ===")
            test_availability_model(doctor)
            print("  Availability model tests passed!")

            print("\n=== Testing Patient Model ===")
            test_patient_model(patient_user)
            print("  Patient model tests passed!")

            patient = Patient.query.filter_by(user_id=patient_user.id).first()

            print("\n=== Testing Appointment Model ===")
            test_appointment_model(doctor, patient)
            print("  Appointment model tests passed!")

            # Get appointment for treatment test
            tomorrow = date.today() + timedelta(days=1)
            apt_time = time(10, 30)
            appointment = Appointment.query.filter_by(
                doctor_id=doctor.id,
                appointment_date=tomorrow,
                appointment_time=apt_time
            ).first()

            print("\n=== Testing Treatment Model ===")
            test_treatment_model(appointment)
            print("  Treatment model tests passed!")

            print("\n" + "=" * 50)
            print("ALL TESTS PASSED!")
            print("=" * 50)

            # Print final summary
            print("\n--- Final Database State ---")
            print(f"Users: {User.query.count()}")
            print(f"Doctors: {Doctor.query.count()}")
            print(f"Patients: {Patient.query.count()}")
            print(f"Departments: {Department.query.count()}")
            print(f"Appointments: {Appointment.query.count()}")
            print(f"Treatments: {Treatment.query.count()}")

        except AssertionError as e:
            print(f"\nTEST FAILED: {e}")
            raise
        except Exception as e:
            print(f"\nERROR: {e}")
            raise


if __name__ == '__main__':
    run_all_tests()
