"""
Test script for verifying all database models and relationships.

Usage:
    python backend/test_models.py
"""
import os
import sys
from datetime import date, time, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.app.models import (
    db, User, Department, Doctor, DoctorAvailability,
    Patient, Appointment, Treatment
)


def test_user_model():
    """Test User model functionality."""
    print("\n=== Testing User Model ===")

    # Test finding admin
    admin = User.find_by_username('admin')
    assert admin is not None, "Admin user not found"
    assert admin.is_admin, "Admin role not set correctly"
    assert admin.check_password('admin123'), "Password check failed"
    print("  - Admin user found and verified")

    # Test creating doctor user
    doctor_user = User(
        username='dr_smith',
        email='dr.smith@hospital.com',
        password='doctor123',
        role='doctor'
    )
    db.session.add(doctor_user)
    db.session.commit()
    assert doctor_user.is_doctor, "Doctor role not set correctly"
    print("  - Doctor user created")

    # Test creating patient user
    patient_user = User(
        username='john_doe',
        email='john@email.com',
        password='patient123',
        role='patient'
    )
    db.session.add(patient_user)
    db.session.commit()
    assert patient_user.is_patient, "Patient role not set correctly"
    print("  - Patient user created")

    # Test find by email
    found = User.find_by_email('dr.smith@hospital.com')
    assert found is not None, "User not found by email"
    print("  - Find by email works")

    print("  User model tests passed!")
    return doctor_user, patient_user


def test_department_model():
    """Test Department model functionality."""
    print("\n=== Testing Department Model ===")

    # Test finding department
    cardiology = Department.find_by_name('Cardiology')
    assert cardiology is not None, "Cardiology department not found"
    print(f"  - Found department: {cardiology.name}")

    # Test get all active
    departments = Department.get_all_active()
    assert len(departments) >= 10, "Not all departments seeded"
    print(f"  - Found {len(departments)} active departments")

    # Test search
    results = Department.search('neuro')
    assert len(results) >= 1, "Search should find Neurology"
    print(f"  - Search for 'neuro' found {len(results)} result(s)")

    print("  Department model tests passed!")
    return cardiology


def test_doctor_model(doctor_user, department):
    """Test Doctor model functionality."""
    print("\n=== Testing Doctor Model ===")

    # Create doctor profile
    doctor = Doctor(
        user_id=doctor_user.id,
        department_id=department.id,
        full_name='Dr. John Smith',
        qualification='MBBS, MD - Cardiology',
        experience_years=15,
        phone='+1234567890',
        bio='Experienced cardiologist specializing in heart diseases.',
        consultation_fee=150.00
    )
    db.session.add(doctor)
    db.session.commit()
    print(f"  - Created doctor: {doctor.full_name}")

    # Test relationships
    assert doctor.user == doctor_user, "User relationship not working"
    assert doctor.department == department, "Department relationship not working"
    assert doctor.email == doctor_user.email, "Email property not working"
    print("  - Relationships verified")

    # Test to_dict
    doctor_dict = doctor.to_dict(include_department=True)
    assert 'department' in doctor_dict, "Department not in dict"
    assert doctor_dict['department']['name'] == 'Cardiology', "Department name incorrect"
    print("  - to_dict works correctly")

    # Test search
    results = Doctor.search(query='Smith')
    assert len(results) >= 1, "Doctor search failed"
    print(f"  - Search for 'Smith' found {len(results)} result(s)")

    print("  Doctor model tests passed!")
    return doctor


def test_availability_model(doctor):
    """Test DoctorAvailability model functionality."""
    print("\n=== Testing DoctorAvailability Model ===")

    today = date.today()
    tomorrow = today + timedelta(days=1)

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
    print(f"  - Set availability for {tomorrow}")

    # Test slot generation
    morning_slots = availability.morning_slots
    evening_slots = availability.evening_slots
    print(f"  - Morning slots: {len(morning_slots)} slots")
    print(f"  - Evening slots: {len(evening_slots)} slots")
    assert len(morning_slots) == 8, f"Expected 8 morning slots, got {len(morning_slots)}"
    assert len(evening_slots) == 10, f"Expected 10 evening slots, got {len(evening_slots)}"

    # Test get_week_availability
    week_avail = DoctorAvailability.get_week_availability(doctor.id)
    assert len(week_avail) >= 1, "Week availability query failed"
    print(f"  - Week availability: {len(week_avail)} day(s)")

    # Test to_dict
    avail_dict = availability.to_dict(include_slots=True)
    assert 'morning_slots' in avail_dict, "Slots not in dict"
    print("  - to_dict works correctly")

    print("  DoctorAvailability model tests passed!")
    return availability


def test_patient_model(patient_user):
    """Test Patient model functionality."""
    print("\n=== Testing Patient Model ===")

    # Create patient profile
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
    print(f"  - Created patient: {patient.full_name}")

    # Test age calculation
    assert patient.age is not None, "Age calculation failed"
    print(f"  - Calculated age: {patient.age}")

    # Test relationships
    assert patient.user == patient_user, "User relationship not working"
    assert patient.email == patient_user.email, "Email property not working"
    print("  - Relationships verified")

    # Test search
    results = Patient.search('John')
    assert len(results) >= 1, "Patient search failed"
    print(f"  - Search for 'John' found {len(results)} result(s)")

    print("  Patient model tests passed!")
    return patient


def test_appointment_model(doctor, patient):
    """Test Appointment model functionality."""
    print("\n=== Testing Appointment Model ===")

    tomorrow = date.today() + timedelta(days=1)
    apt_time = time(9, 0)

    # Create appointment
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
    print(f"  - Created appointment for {tomorrow} at {apt_time}")

    # Test relationships
    assert appointment.patient == patient, "Patient relationship not working"
    assert appointment.doctor == doctor, "Doctor relationship not working"
    print("  - Relationships verified")

    # Test properties
    assert appointment.is_upcoming, "is_upcoming should be True"
    assert appointment.can_cancel, "can_cancel should be True"
    assert appointment.status == 'booked', "Status should be 'booked'"
    print("  - Properties verified")

    # Test slot availability
    is_available = Appointment.check_slot_available(doctor.id, tomorrow, apt_time)
    assert not is_available, "Slot should not be available"
    print("  - Slot availability check works")

    # Test booked slots
    booked = Appointment.get_booked_slots(doctor.id, tomorrow)
    assert apt_time in booked, "Booked slot not returned"
    print(f"  - Found {len(booked)} booked slot(s)")

    # Test double booking prevention (unique constraint)
    try:
        duplicate = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=tomorrow,
            appointment_time=apt_time,
            reason='Another booking'
        )
        db.session.add(duplicate)
        db.session.commit()
        assert False, "Should have raised an error for double booking"
    except Exception:
        db.session.rollback()
        print("  - Double booking prevention works")

    print("  Appointment model tests passed!")
    return appointment


def test_treatment_model(appointment):
    """Test Treatment model functionality."""
    print("\n=== Testing Treatment Model ===")

    # First complete the appointment
    appointment.complete()
    db.session.commit()
    assert appointment.status == 'completed', "Appointment not marked completed"
    print("  - Appointment marked as completed")

    # Create treatment
    treatment = Treatment(
        appointment_id=appointment.id,
        diagnosis='Mild hypertension',
        prescription='Amlodipine 5mg\nAspirin 75mg',
        notes='Patient advised to reduce salt intake and exercise regularly.',
        tests_recommended='ECG\nBlood pressure monitoring',
        follow_up_date=date.today() + timedelta(days=30),
        visit_type='in-person'
    )
    db.session.add(treatment)
    db.session.commit()
    print(f"  - Created treatment for appointment {appointment.id}")

    # Test relationships
    assert treatment.appointment == appointment, "Appointment relationship not working"
    assert treatment.patient == appointment.patient, "Patient access not working"
    assert treatment.doctor == appointment.doctor, "Doctor access not working"
    print("  - Relationships verified")

    # Test prescription list
    meds = treatment.get_prescription_list()
    assert len(meds) == 2, "Prescription parsing failed"
    print(f"  - Parsed {len(meds)} medications")

    # Test patient history
    history = Treatment.get_patient_history(appointment.patient_id)
    assert len(history) >= 1, "Patient history query failed"
    print(f"  - Found {len(history)} treatment(s) in patient history")

    # Test export dict
    export = treatment.to_export_dict()
    assert 'diagnosis' in export, "Export dict missing fields"
    print("  - Export dict works correctly")

    print("  Treatment model tests passed!")
    return treatment


def run_all_tests():
    """Run all model tests."""
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 50)
        print("Hospital Management System - Model Tests")
        print("=" * 50)

        try:
            # Run tests in order (dependencies matter)
            doctor_user, patient_user = test_user_model()
            department = test_department_model()
            doctor = test_doctor_model(doctor_user, department)
            availability = test_availability_model(doctor)
            patient = test_patient_model(patient_user)
            appointment = test_appointment_model(doctor, patient)
            treatment = test_treatment_model(appointment)

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
