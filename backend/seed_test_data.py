
import os
import sys
import random
from datetime import datetime, timedelta, time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.app.models import db, User, Department, Doctor, Patient, Appointment, Treatment, Payment

# Test data for doctors
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

# Test data for patients
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

# Appointment reasons
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


def seed_doctors():
    
    print("\n--- Seeding Doctors ---")
    created = 0

    for doc_data in DOCTORS_DATA:
        # Check if doctor already exists
        username = f"dr_{doc_data['last_name'].lower()}"
        existing = User.find_by_username(username)

        if existing:
            print(f"  Doctor {username} already exists, skipping...")
            continue

        # Get department
        dept = Department.find_by_name(doc_data['department'])
        if not dept:
            print(f"  Department {doc_data['department']} not found, skipping {username}...")
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
        db.session.flush()  # Get user ID

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
        print(f"  Created doctor: Dr. {doc_data['first_name']} {doc_data['last_name']} ({doc_data['department']})")

    db.session.commit()
    print(f"\nCreated {created} new doctors.")
    return created


def seed_patients():
    
    print("\n--- Seeding Patients ---")
    created = 0

    for pat_data in PATIENTS_DATA:
        # Check if patient already exists
        username = f"{pat_data['first_name'].lower()}_{pat_data['last_name'].lower()}"
        existing = User.find_by_username(username)

        if existing:
            print(f"  Patient {username} already exists, skipping...")
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
        print(f"  Created patient: {pat_data['first_name']} {pat_data['last_name']}")

    db.session.commit()
    print(f"\nCreated {created} new patients.")
    return created


def seed_appointments():
    
    print("\n--- Seeding Appointments ---")

    doctors = Doctor.query.filter_by(is_active=True).all()
    patients = Patient.query.all()

    if not doctors or not patients:
        print("  No doctors or patients found. Run seed_doctors and seed_patients first.")
        return 0

    created = 0
    statuses = ['completed', 'completed', 'completed', 'scheduled', 'scheduled', 'cancelled']
    time_slots = [
        time(9, 0), time(9, 30), time(10, 0), time(10, 30), time(11, 0), time(11, 30),
        time(14, 0), time(14, 30), time(15, 0), time(15, 30), time(16, 0)
    ]

    # Create appointments for each patient
    for patient in patients:
        # 2-4 appointments per patient
        num_appointments = random.randint(2, 4)

        for _ in range(num_appointments):
            doctor = random.choice(doctors)

            # Random date: past 30 days to next 14 days
            days_offset = random.randint(-30, 14)
            appt_date = datetime.now().date() + timedelta(days=days_offset)

            # Skip weekends
            if appt_date.weekday() >= 5:
                continue

            # Check if appointment already exists for this slot
            time_slot = random.choice(time_slots)
            existing = Appointment.query.filter_by(
                doctor_id=doctor.id,
                appointment_date=appt_date,
                appointment_time=time_slot
            ).first()

            if existing:
                continue

            # Determine status based on date
            if days_offset < 0:
                status = random.choice(['completed', 'completed', 'cancelled'])
            else:
                status = 'booked'  # Future appointments are booked

            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                department_id=doctor.department_id,
                appointment_date=appt_date,
                appointment_time=time_slot,
                reason=random.choice(APPOINTMENT_REASONS)
            )
            appointment.status = status  # Set status after creation

            # Add notes for completed appointments
            if status == 'completed':
                appointment.notes = "Patient consultation completed. Follow-up recommended in 2 weeks."

            db.session.add(appointment)
            created += 1

    db.session.commit()
    print(f"Created {created} appointments.")
    return created


def seed_treatments():
    
    print("\n--- Seeding Treatments ---")

    completed_appointments = Appointment.query.filter_by(status='completed').all()
    created = 0

    diagnoses = [
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

    prescriptions = [
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

    tests_recommended = [
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

    visit_types = ['in-person', 'follow-up', 'routine-checkup']

    for appt in completed_appointments:
        # Check if treatment already exists
        existing = Treatment.query.filter_by(appointment_id=appt.id).first()
        if existing:
            continue

        treatment = Treatment(
            appointment_id=appt.id,
            diagnosis=random.choice(diagnoses),
            prescription=random.choice(prescriptions),
            notes="Patient examined. Vital signs normal. Recommended follow-up in 4-6 weeks.",
            tests_recommended=random.choice(tests_recommended),
            follow_up_date=(appt.appointment_date + timedelta(days=random.randint(14, 42))),
            visit_type=random.choice(visit_types)
        )
        db.session.add(treatment)
        created += 1

    db.session.commit()
    print(f"Created {created} treatment records.")
    return created


def seed_payments():
    
    print("\n--- Seeding Payments ---")

    completed_appointments = Appointment.query.filter_by(status='completed').all()
    created = 0

    payment_methods = ['credit_card', 'debit_card', 'cash', 'insurance']

    for appt in completed_appointments:
        # Check if payment already exists
        existing = Payment.query.filter_by(appointment_id=appt.id).first()
        if existing:
            continue

        doctor = Doctor.query.get(appt.doctor_id)
        if not doctor:
            continue

        # Randomly decide if payment is completed or pending
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
    return created


def print_summary():
    """Print summary of database contents."""
    print("\n" + "="*50)
    print("DATABASE SUMMARY")
    print("="*50)

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

    print("\n--- Doctors by Department ---")
    for dept in Department.query.order_by(Department.name).all():
        doc_count = Doctor.query.filter_by(department_id=dept.id, is_active=True).count()
        print(f"  {dept.name}: {doc_count} doctor(s)")

    print("\n--- Sample Credentials ---")
    print("Admin: admin / admin123")
    print("Doctor: dr_chen / doctor123")
    print("Patient: john_smith / patient123")


def main():
    """Main function to seed all test data."""
    print("="*50)
    print("SEEDING TEST DATA FOR HMS")
    print("="*50)

    app = create_app()

    with app.app_context():
        # Seed in order
        seed_doctors()
        seed_patients()
        seed_appointments()
        seed_treatments()
        seed_payments()

        # Print summary
        print_summary()

    print("\n" + "="*50)
    print("SEEDING COMPLETE!")
    print("="*50)


if __name__ == '__main__':
    main()
