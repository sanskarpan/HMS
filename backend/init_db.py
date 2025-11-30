"""
Database initialization script for the Hospital Management System.

This script:
1. Creates all database tables
2. Creates the admin user (programmatically as required)
3. Seeds default departments
4. Seeds sample doctors, patients, appointments, treatments, and payments

Usage:
    python backend/init_db.py
    python backend/init_db.py --reset  # Reset database (development only)
    python backend/init_db.py --no-sample-data  # Skip sample data seeding
"""
import os
import sys
import random
from datetime import datetime, timedelta, time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.app.models import db, User, Department, Doctor, Patient, Appointment, Treatment, Payment
from backend.app.models.availability import DoctorAvailability
from backend.app.models.status_log import AppointmentStatusLog
from backend.app.models.department import DEFAULT_DEPARTMENTS
from backend.config import Config


DOCTORS_DATA = [
    # Cardiology
    {"first_name": "Michael", "last_name": "Chen", "department": "Cardiology", "qualification": "MD, FACC", "experience": 15, "fee": 200, "bio": "Board-certified cardiologist specializing in interventional cardiology and heart failure management."},
    {"first_name": "Sarah", "last_name": "Johnson", "department": "Cardiology", "qualification": "MD, PhD", "experience": 12, "fee": 180, "bio": "Expert in cardiac imaging and preventive cardiology with research focus on heart disease prevention."},

    # Oncology
    {"first_name": "David", "last_name": "Williams", "department": "Oncology", "qualification": "MD, FASCO", "experience": 18, "fee": 250, "bio": "Renowned oncologist specializing in breast cancer and immunotherapy treatments."},
    {"first_name": "Emily", "last_name": "Brown", "department": "Oncology", "qualification": "MD, PhD", "experience": 10, "fee": 220, "bio": "Specialist in pediatric oncology and targeted cancer therapies."},

    # General Medicine
    {"first_name": "James", "last_name": "Miller", "department": "General Medicine", "qualification": "MD, FACP", "experience": 20, "fee": 120, "bio": "Experienced internist providing comprehensive primary care for adults."},
    {"first_name": "Jennifer", "last_name": "Davis", "department": "General Medicine", "qualification": "MD", "experience": 8, "fee": 100, "bio": "Family medicine specialist focused on preventive care and chronic disease management."},
    {"first_name": "Robert", "last_name": "Garcia", "department": "General Medicine", "qualification": "DO", "experience": 14, "fee": 110, "bio": "Holistic approach to internal medicine with expertise in geriatric care."},

    # Orthopedics
    {"first_name": "William", "last_name": "Martinez", "department": "Orthopedics", "qualification": "MD, FAAOS", "experience": 16, "fee": 200, "bio": "Orthopedic surgeon specializing in sports medicine and joint replacement."},
    {"first_name": "Jessica", "last_name": "Anderson", "department": "Orthopedics", "qualification": "MD", "experience": 9, "fee": 180, "bio": "Expert in minimally invasive spine surgery and pediatric orthopedics."},

    # Pediatrics
    {"first_name": "Christopher", "last_name": "Taylor", "department": "Pediatrics", "qualification": "MD, FAAP", "experience": 13, "fee": 130, "bio": "Dedicated pediatrician with special interest in developmental pediatrics and adolescent medicine."},
    {"first_name": "Amanda", "last_name": "Thomas", "department": "Pediatrics", "qualification": "MD", "experience": 7, "fee": 120, "bio": "Caring pediatrician focusing on newborn care and childhood immunizations."},
    {"first_name": "Daniel", "last_name": "Jackson", "department": "Pediatrics", "qualification": "DO", "experience": 11, "fee": 125, "bio": "Pediatric specialist with expertise in childhood allergies and asthma."},

    # Dermatology
    {"first_name": "Michelle", "last_name": "White", "department": "Dermatology", "qualification": "MD, FAAD", "experience": 14, "fee": 175, "bio": "Board-certified dermatologist specializing in skin cancer detection and cosmetic dermatology."},
    {"first_name": "Kevin", "last_name": "Harris", "department": "Dermatology", "qualification": "MD", "experience": 8, "fee": 160, "bio": "Expert in treating acne, eczema, and psoriasis with both traditional and innovative therapies."},

    # Neurology
    {"first_name": "Patricia", "last_name": "Clark", "department": "Neurology", "qualification": "MD, PhD", "experience": 17, "fee": 220, "bio": "Neurologist specializing in stroke treatment, epilepsy, and movement disorders."},
    {"first_name": "Andrew", "last_name": "Lewis", "department": "Neurology", "qualification": "MD", "experience": 12, "fee": 200, "bio": "Expert in headache medicine and multiple sclerosis management."},

    # Psychiatry
    {"first_name": "Elizabeth", "last_name": "Robinson", "department": "Psychiatry", "qualification": "MD, DFAPA", "experience": 19, "fee": 190, "bio": "Distinguished psychiatrist with expertise in mood disorders and anxiety treatment."},
    {"first_name": "Matthew", "last_name": "Walker", "department": "Psychiatry", "qualification": "MD", "experience": 10, "fee": 170, "bio": "Specialist in addiction psychiatry and trauma-informed care."},

    # Gynecology
    {"first_name": "Linda", "last_name": "Hall", "department": "Gynecology", "qualification": "MD, FACOG", "experience": 15, "fee": 180, "bio": "Experienced OB-GYN specializing in high-risk pregnancies and minimally invasive surgery."},
    {"first_name": "Rachel", "last_name": "Allen", "department": "Gynecology", "qualification": "MD", "experience": 9, "fee": 165, "bio": "Women's health specialist focusing on reproductive endocrinology and fertility."},

    # Ophthalmology
    {"first_name": "Thomas", "last_name": "Young", "department": "Ophthalmology", "qualification": "MD, FACS", "experience": 21, "fee": 200, "bio": "Leading ophthalmologist specializing in cataract surgery and LASIK procedures."},
    {"first_name": "Nancy", "last_name": "King", "department": "Ophthalmology", "qualification": "MD", "experience": 11, "fee": 185, "bio": "Expert in glaucoma management and retinal diseases."},
]

PATIENTS_DATA = [
    {"first_name": "John", "last_name": "Smith", "email": "john.smith@email.com", "phone": "555-0101", "dob": "1985-03-15", "gender": "male", "blood_group": "A+", "address": "123 Main St, Springfield"},
    {"first_name": "Mary", "last_name": "Johnson", "email": "mary.j@email.com", "phone": "555-0102", "dob": "1990-07-22", "gender": "female", "blood_group": "B+", "address": "456 Oak Ave, Riverside"},
    {"first_name": "Robert", "last_name": "Williams", "email": "rwilliams@email.com", "phone": "555-0103", "dob": "1978-11-08", "gender": "male", "blood_group": "O+", "address": "789 Pine Rd, Lakeside"},
    {"first_name": "Patricia", "last_name": "Brown", "email": "pbrown@email.com", "phone": "555-0104", "dob": "1995-02-28", "gender": "female", "blood_group": "AB+", "address": "321 Elm St, Hilltown"},
    {"first_name": "Michael", "last_name": "Jones", "email": "mjones@email.com", "phone": "555-0105", "dob": "1982-09-14", "gender": "male", "blood_group": "A-", "address": "654 Maple Dr, Valleyview"},
    {"first_name": "Jennifer", "last_name": "Garcia", "email": "jgarcia@email.com", "phone": "555-0106", "dob": "1988-12-03", "gender": "female", "blood_group": "B-", "address": "987 Cedar Ln, Mountainside"},
    {"first_name": "David", "last_name": "Miller", "email": "dmiller@email.com", "phone": "555-0107", "dob": "1970-05-20", "gender": "male", "blood_group": "O-", "address": "147 Birch Way, Seaside"},
    {"first_name": "Linda", "last_name": "Davis", "email": "ldavis@email.com", "phone": "555-0108", "dob": "1992-08-11", "gender": "female", "blood_group": "AB-", "address": "258 Walnut Ct, Parkview"},
    {"first_name": "James", "last_name": "Rodriguez", "email": "jrod@email.com", "phone": "555-0109", "dob": "1975-01-30", "gender": "male", "blood_group": "A+", "address": "369 Spruce Blvd, Greendale"},
    {"first_name": "Barbara", "last_name": "Martinez", "email": "bmartinez@email.com", "phone": "555-0110", "dob": "1998-06-17", "gender": "female", "blood_group": "B+", "address": "741 Willow St, Sunnyvale"},
]

APPOINTMENT_REASONS = [
    "Annual checkup",
    "Follow-up visit",
    "New patient consultation",
    "Persistent headache",
    "Back pain",
    "Skin rash evaluation",
    "Blood pressure monitoring",
    "Chest discomfort",
    "Joint pain assessment",
    "Routine vaccination",
    "Eye examination",
    "Mental health consultation",
    "Pregnancy checkup",
    "Diabetes management",
    "Allergy testing",
]

DIAGNOSES = [
    "Hypertension - Stage 1",
    "Type 2 Diabetes Mellitus",
    "Upper Respiratory Infection",
    "Migraine without aura",
    "Seasonal Allergies",
    "Lower Back Pain - Mechanical",
    "Anxiety Disorder",
    "Eczema - Mild",
    "Vitamin D Deficiency",
    "Gastroesophageal Reflux Disease",
]

PRESCRIPTIONS = [
    "Lisinopril 10mg - Once daily\nAspirin 81mg - Once daily",
    "Metformin 500mg - Twice daily with meals\nGlucometer supplies",
    "Amoxicillin 500mg - Three times daily for 7 days\nRest and fluids",
    "Sumatriptan 50mg - As needed for migraine\nAvoid triggers",
    "Cetirizine 10mg - Once daily\nNasal saline spray",
    "Ibuprofen 400mg - As needed\nPhysical therapy referral",
    "Sertraline 50mg - Once daily\nCognitive behavioral therapy referral",
    "Hydrocortisone 1% cream - Apply twice daily\nMoisturizer",
    "Vitamin D3 2000 IU - Once daily\nSun exposure 15min/day",
    "Omeprazole 20mg - Once daily before breakfast\nDietary modifications",
]

TESTS_RECOMMENDED = [
    "Complete Blood Count (CBC)\nLipid Profile",
    "HbA1c test\nFasting Blood Glucose",
    "Chest X-Ray if symptoms persist",
    "MRI Brain if headaches worsen",
    "Allergy panel testing",
    "Spine X-Ray\nPhysical therapy evaluation",
    "Thyroid function tests",
    "Skin biopsy if needed",
    "Vitamin D levels recheck in 3 months",
    "Upper GI endoscopy if symptoms persist",
]


def init_database(reset=False, seed_sample_data=True):
    """
    Initialize the database with tables, admin user, and default data.

    Args:
        reset: If True, drop all tables before creating (development only)
        seed_sample_data: If True, seed sample doctors, patients, appointments
    """
    app = create_app()

    with app.app_context():
        if reset:
            print("Dropping all tables...")
            db.drop_all()

        print("Creating database tables...")
        db.create_all()

        # Create admin user if not exists
        create_admin_user()

        # Seed default departments
        seed_departments()

        if seed_sample_data:
            print("\n--- Seeding Sample Data ---")
            seed_doctors()
            seed_patients()
            seed_appointments()
            seed_treatments()
            seed_payments()
            seed_doctor_availability()
            seed_status_logs()

        print("\nDatabase initialization complete!")
        print_summary()


def create_admin_user():
    """Create the admin user if it doesn't exist."""
    admin = User.find_by_username(Config.ADMIN_USERNAME)

    if admin:
        print(f"Admin user '{Config.ADMIN_USERNAME}' already exists.")
        return admin

    print("Creating admin user...")
    admin = User(
        username=Config.ADMIN_USERNAME,
        email=Config.ADMIN_EMAIL,
        password=Config.ADMIN_PASSWORD,
        role='admin'
    )
    admin.is_active = True

    db.session.add(admin)
    db.session.commit()

    print(f"Admin user created:")
    print(f"  Username: {Config.ADMIN_USERNAME}")
    print(f"  Email: {Config.ADMIN_EMAIL}")
    print(f"  Password: {Config.ADMIN_PASSWORD}")

    return admin


def seed_departments():
    """Seed default departments if they don't exist."""
    print("Seeding departments...")

    created_count = 0
    for dept_data in DEFAULT_DEPARTMENTS:
        existing = Department.find_by_name(dept_data['name'])
        if not existing:
            dept = Department(
                name=dept_data['name'],
                description=dept_data['description']
            )
            db.session.add(dept)
            created_count += 1

    db.session.commit()

    if created_count > 0:
        print(f"Created {created_count} new departments.")
    else:
        print("All departments already exist.")


def seed_doctors():
    """Create doctor users and profiles."""
    print("Seeding doctors...")
    created = 0

    for doc_data in DOCTORS_DATA:
        username = f"dr_{doc_data['last_name'].lower()}"
        existing = User.find_by_username(username)

        if existing:
            continue

        dept = Department.find_by_name(doc_data['department'])
        if not dept:
            continue

        # Create user
        user = User(
            username=username,
            email=f"{username}@hospital.com",
            password="doctor123",
            role='doctor'
        )
        user.is_active = True
        db.session.add(user)
        db.session.flush()

        # Create doctor profile
        full_name = f"{doc_data['first_name']} {doc_data['last_name']}"
        doctor = Doctor(
            user_id=user.id,
            department_id=dept.id,
            full_name=full_name,
            qualification=doc_data['qualification'],
            experience_years=doc_data['experience'],
            consultation_fee=doc_data['fee'],
            bio=doc_data['bio'],
            phone=f"555-{random.randint(1000, 9999)}"
        )
        doctor.is_active = True
        db.session.add(doctor)
        created += 1

    db.session.commit()
    print(f"Created {created} doctors.")


def seed_patients():
    """Create patient users and profiles."""
    print("Seeding patients...")
    created = 0

    for pat_data in PATIENTS_DATA:
        username = f"{pat_data['first_name'].lower()}_{pat_data['last_name'].lower()}"
        existing = User.find_by_username(username)

        if existing:
            continue

        # Create user
        user = User(
            username=username,
            email=pat_data['email'],
            password="patient123",
            role='patient'
        )
        user.is_active = True
        db.session.add(user)
        db.session.flush()

        # Create patient profile
        full_name = f"{pat_data['first_name']} {pat_data['last_name']}"
        patient = Patient(
            user_id=user.id,
            full_name=full_name,
            phone=pat_data['phone'],
            date_of_birth=datetime.strptime(pat_data['dob'], '%Y-%m-%d').date(),
            gender=pat_data['gender'],
            blood_group=pat_data['blood_group'],
            address=pat_data['address']
        )
        db.session.add(patient)
        created += 1

    db.session.commit()
    print(f"Created {created} patients.")


def seed_appointments():
    """Create sample appointments (past and future)."""
    print("Seeding appointments...")

    doctors = Doctor.query.filter_by(is_active=True).all()
    patients = Patient.query.all()

    if not doctors or not patients:
        print("  No doctors or patients found.")
        return

    created = 0
    time_slots = [
        time(9, 0), time(9, 30), time(10, 0), time(10, 30), time(11, 0), time(11, 30),
        time(14, 0), time(14, 30), time(15, 0), time(15, 30), time(16, 0)
    ]

    for patient in patients:
        num_appointments = random.randint(2, 4)

        for _ in range(num_appointments):
            doctor = random.choice(doctors)
            days_offset = random.randint(-30, 14)
            appt_date = datetime.now().date() + timedelta(days=days_offset)

            if appt_date.weekday() >= 5:
                continue

            time_slot = random.choice(time_slots)
            existing = Appointment.query.filter_by(
                doctor_id=doctor.id,
                appointment_date=appt_date,
                appointment_time=time_slot
            ).first()

            if existing:
                continue

            if days_offset < 0:
                status = random.choice(['completed', 'completed', 'cancelled'])
            else:
                status = 'booked'

            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                department_id=doctor.department_id,
                appointment_date=appt_date,
                appointment_time=time_slot,
                reason=random.choice(APPOINTMENT_REASONS)
            )
            appointment.status = status

            if status == 'completed':
                appointment.notes = "Patient consultation completed. Follow-up recommended in 2 weeks."

            db.session.add(appointment)
            created += 1

    db.session.commit()
    print(f"Created {created} appointments.")


def seed_treatments():
    """Create sample treatment records for completed appointments."""
    print("Seeding treatments...")

    completed_appointments = Appointment.query.filter_by(status='completed').all()
    created = 0

    visit_types = ['in-person', 'follow-up', 'routine-checkup']

    for appt in completed_appointments:
        existing = Treatment.query.filter_by(appointment_id=appt.id).first()
        if existing:
            continue

        treatment = Treatment(
            appointment_id=appt.id,
            diagnosis=random.choice(DIAGNOSES),
            prescription=random.choice(PRESCRIPTIONS),
            notes="Patient examined. Vital signs normal. Recommended follow-up in 4-6 weeks.",
            tests_recommended=random.choice(TESTS_RECOMMENDED),
            follow_up_date=(appt.appointment_date + timedelta(days=random.randint(14, 42))),
            visit_type=random.choice(visit_types)
        )
        db.session.add(treatment)
        created += 1

    db.session.commit()
    print(f"Created {created} treatments.")


def seed_payments():
    """Create sample payments for completed appointments."""
    print("Seeding payments...")

    completed_appointments = Appointment.query.filter_by(status='completed').all()
    created = 0

    payment_methods = ['credit_card', 'debit_card', 'cash', 'insurance']

    for appt in completed_appointments:
        existing = Payment.query.filter_by(appointment_id=appt.id).first()
        if existing:
            continue

        doctor = db.session.get(Doctor, appt.doctor_id)
        if not doctor:
            continue

        status = random.choice(['completed', 'completed', 'completed', 'pending'])

        payment = Payment(
            patient_id=appt.patient_id,
            appointment_id=appt.id,
            amount=float(doctor.consultation_fee or 100),
            payment_method=random.choice(payment_methods) if status == 'completed' else None,
            status=status,
            description=f"Consultation fee for appointment on {appt.appointment_date}"
        )

        if status == 'completed':
            payment.paid_at = datetime.combine(appt.appointment_date, datetime.min.time()) + timedelta(hours=random.randint(9, 17))
            payment.transaction_id = f"TXN{random.randint(100000, 999999)}"

        db.session.add(payment)
        created += 1

    db.session.commit()
    print(f"Created {created} payments.")


def seed_doctor_availability():
    """Create availability schedules for all doctors for the next 14 days."""
    print("Seeding doctor availability...")

    doctors = Doctor.query.filter_by(is_active=True).all()
    created = 0

    # Working hours configurations (some variation for realism)
    work_schedules = [
        # Standard morning + evening
        {"morning": (time(9, 0), time(12, 0)), "evening": (time(14, 0), time(17, 0))},
        # Early morning + afternoon
        {"morning": (time(8, 0), time(11, 0)), "evening": (time(13, 0), time(16, 0))},
        # Late morning + late evening
        {"morning": (time(10, 0), time(13, 0)), "evening": (time(15, 0), time(18, 0))},
        # Morning only
        {"morning": (time(9, 0), time(13, 0)), "evening": None},
        # Evening only
        {"morning": None, "evening": (time(14, 0), time(19, 0))},
    ]

    for doctor in doctors:
        # Each doctor gets a consistent schedule type
        schedule = work_schedules[doctor.id % len(work_schedules)]

        # Create availability for next 14 days
        for day_offset in range(14):
            avail_date = datetime.now().date() + timedelta(days=day_offset)

            # Skip weekends for most doctors (some work Saturdays)
            if avail_date.weekday() == 6:  # Sunday - no one works
                continue
            if avail_date.weekday() == 5 and doctor.id % 3 != 0:  # Saturday - only some doctors
                continue

            # Check if availability already exists
            existing = DoctorAvailability.query.filter_by(
                doctor_id=doctor.id,
                date=avail_date
            ).first()

            if existing:
                continue

            # Random day off for variety (about 1 in 10 weekdays)
            if random.random() < 0.1:
                continue

            availability = DoctorAvailability(
                doctor_id=doctor.id,
                date=avail_date,
                slot_duration=30
            )

            if schedule["morning"]:
                availability.start_time_morning = schedule["morning"][0]
                availability.end_time_morning = schedule["morning"][1]

            if schedule["evening"]:
                availability.start_time_evening = schedule["evening"][0]
                availability.end_time_evening = schedule["evening"][1]

            db.session.add(availability)
            created += 1

    db.session.commit()
    print(f"Created {created} doctor availability records.")


def seed_status_logs():
    """Create status change logs for appointments."""
    print("Seeding appointment status logs...")

    appointments = Appointment.query.all()
    created = 0

    for appt in appointments:
        # Check if logs already exist for this appointment
        existing = AppointmentStatusLog.query.filter_by(appointment_id=appt.id).first()
        if existing:
            continue

        # Initial booking log
        initial_log = AppointmentStatusLog(
            appointment_id=appt.id,
            old_status=None,
            new_status='booked',
            changed_by_id=appt.patient_id,
            changed_by_role='patient',
            reason='Appointment booked by patient'
        )
        # Set created_at to before appointment date
        days_before = random.randint(1, 7)
        initial_log.created_at = datetime.combine(
            appt.appointment_date - timedelta(days=days_before),
            time(random.randint(9, 17), random.randint(0, 59))
        )
        db.session.add(initial_log)
        created += 1

        # Status change logs for non-booked appointments
        if appt.status == 'completed':
            complete_log = AppointmentStatusLog(
                appointment_id=appt.id,
                old_status='booked',
                new_status='completed',
                changed_by_id=appt.doctor_id,
                changed_by_role='doctor',
                reason='Consultation completed successfully'
            )
            complete_log.created_at = datetime.combine(
                appt.appointment_date,
                time(random.randint(9, 17), random.randint(0, 59))
            )
            db.session.add(complete_log)
            created += 1

        elif appt.status == 'cancelled':
            cancel_reasons = [
                'Patient requested cancellation',
                'Schedule conflict',
                'Doctor unavailable',
                'Patient illness',
                'Emergency rescheduling'
            ]
            cancelled_by_role = random.choice(['patient', 'doctor', 'admin'])
            cancel_log = AppointmentStatusLog(
                appointment_id=appt.id,
                old_status='booked',
                new_status='cancelled',
                changed_by_id=appt.patient_id if cancelled_by_role == 'patient' else appt.doctor_id,
                changed_by_role=cancelled_by_role,
                reason=random.choice(cancel_reasons)
            )
            cancel_log.created_at = datetime.combine(
                appt.appointment_date - timedelta(days=random.randint(0, 2)),
                time(random.randint(9, 17), random.randint(0, 59))
            )
            db.session.add(cancel_log)
            created += 1

        elif appt.status == 'no_show':
            no_show_log = AppointmentStatusLog(
                appointment_id=appt.id,
                old_status='booked',
                new_status='no_show',
                changed_by_id=appt.doctor_id,
                changed_by_role='doctor',
                reason='Patient did not attend scheduled appointment'
            )
            no_show_log.created_at = datetime.combine(
                appt.appointment_date,
                time(random.randint(16, 18), random.randint(0, 59))
            )
            db.session.add(no_show_log)
            created += 1

    db.session.commit()
    print(f"Created {created} appointment status logs.")


def print_summary():
    """Print summary of database contents."""
    print("\n" + "=" * 50)
    print("DATABASE SUMMARY")
    print("=" * 50)

    print(f"\nUsers: {User.query.count()}")
    print(f"  - Admins: {User.query.filter_by(role='admin').count()}")
    print(f"  - Doctors: {User.query.filter_by(role='doctor').count()}")
    print(f"  - Patients: {User.query.filter_by(role='patient').count()}")

    print(f"\nDepartments: {Department.query.count()}")
    print(f"Doctors: {Doctor.query.count()}")
    print(f"Patients: {Patient.query.count()}")
    print(f"Appointments: {Appointment.query.count()}")
    print(f"Treatments: {Treatment.query.count()}")
    print(f"Payments: {Payment.query.count()}")
    print(f"Doctor Availability Records: {DoctorAvailability.query.count()}")
    print(f"Appointment Status Logs: {AppointmentStatusLog.query.count()}")

    print("\n--- Doctors by Department ---")
    for dept in Department.query.order_by(Department.name).all():
        doc_count = Doctor.query.filter_by(department_id=dept.id, is_active=True).count()
        if doc_count > 0:
            print(f"  {dept.name}: {doc_count} doctor(s)")

    print("\n--- Sample Credentials ---")
    print(f"Admin: {Config.ADMIN_USERNAME} / {Config.ADMIN_PASSWORD}")
    print("Doctor: dr_chen / doctor123")
    print("Patient: john_smith / patient123")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Initialize the Hospital Management System database')
    parser.add_argument('--reset', action='store_true',
                        help='Reset database (drops all tables - development only)')
    parser.add_argument('--no-sample-data', action='store_true',
                        help='Skip seeding sample data (doctors, patients, appointments)')

    args = parser.parse_args()

    if args.reset:
        confirm = input("WARNING: This will delete all data. Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)

    init_database(reset=args.reset, seed_sample_data=not args.no_sample_data)
