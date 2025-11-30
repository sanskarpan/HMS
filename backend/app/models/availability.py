from datetime import datetime, date, time, timedelta
from . import db, TimestampMixin


class DoctorAvailability(db.Model, TimestampMixin):
    __tablename__ = 'doctor_availability'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)

    # Morning slot times
    start_time_morning = db.Column(db.Time, nullable=True)
    end_time_morning = db.Column(db.Time, nullable=True)

    # Evening slot times
    start_time_evening = db.Column(db.Time, nullable=True)
    end_time_evening = db.Column(db.Time, nullable=True)

    # Status and configuration
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    slot_duration = db.Column(db.Integer, default=30, nullable=False)  # minutes

    # Unique constraint: one availability record per doctor per date
    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'date', name='unique_doctor_date'),
    )

    # Relationships
    doctor = db.relationship('Doctor', back_populates='availability')

    def __init__(self, doctor_id, date, **kwargs):
        """Initialize availability for a doctor on a specific date."""
        self.doctor_id = doctor_id
        self.date = date
        self.start_time_morning = kwargs.get('start_time_morning')
        self.end_time_morning = kwargs.get('end_time_morning')
        self.start_time_evening = kwargs.get('start_time_evening')
        self.end_time_evening = kwargs.get('end_time_evening')
        self.is_available = kwargs.get('is_available', True)
        self.slot_duration = kwargs.get('slot_duration', 30)

    def _generate_slots(self, start_time, end_time):
        """Generate time slots between start and end times."""
        if not start_time or not end_time:
            return []

        slots = []
        current = datetime.combine(self.date, start_time)
        end = datetime.combine(self.date, end_time)
        duration = timedelta(minutes=self.slot_duration)

        while current + duration <= end:
            slots.append(current.time())
            current += duration

        return slots

    @property
    def morning_slots(self):
        """Get available morning time slots."""
        return self._generate_slots(self.start_time_morning, self.end_time_morning)

    @property
    def evening_slots(self):
        """Get available evening time slots."""
        return self._generate_slots(self.start_time_evening, self.end_time_evening)

    @property
    def all_slots(self):
        """Get all available time slots for the day."""
        return self.morning_slots + self.evening_slots

    def get_available_slots(self, booked_times=None):
        """
        Get available slots excluding already booked times.

        Args:
            booked_times: List of time objects that are already booked

        Returns:
            List of available time slots
        """
        if booked_times is None:
            booked_times = []

        all_slots = self.all_slots
        return [slot for slot in all_slots if slot not in booked_times]

    def is_slot_available(self, slot_time):
        """Check if a specific time slot is within available hours."""
        if not self.is_available:
            return False

        # Check morning slots
        if self.start_time_morning and self.end_time_morning:
            if self.start_time_morning <= slot_time < self.end_time_morning:
                return True

        # Check evening slots
        if self.start_time_evening and self.end_time_evening:
            if self.start_time_evening <= slot_time < self.end_time_evening:
                return True

        return False

    def to_dict(self, include_slots=False):
        """Convert availability to dictionary representation."""
        data = {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time_morning': self.start_time_morning.strftime('%H:%M') if self.start_time_morning else None,
            'end_time_morning': self.end_time_morning.strftime('%H:%M') if self.end_time_morning else None,
            'start_time_evening': self.start_time_evening.strftime('%H:%M') if self.start_time_evening else None,
            'end_time_evening': self.end_time_evening.strftime('%H:%M') if self.end_time_evening else None,
            'is_available': self.is_available,
            'slot_duration': self.slot_duration
        }

        if include_slots:
            data['morning_slots'] = [s.strftime('%H:%M') for s in self.morning_slots]
            data['evening_slots'] = [s.strftime('%H:%M') for s in self.evening_slots]

        return data

    def __repr__(self):
        return f'<DoctorAvailability Doctor:{self.doctor_id} Date:{self.date}>'

    @classmethod
    def get_for_doctor_and_date(cls, doctor_id, date):
        """Get availability for a specific doctor and date."""
        return cls.query.filter_by(doctor_id=doctor_id, date=date).first()

    @classmethod
    def get_week_availability(cls, doctor_id, start_date=None):
        """Get 7-day availability for a doctor starting from a date."""
        if start_date is None:
            start_date = date.today()

        end_date = start_date + timedelta(days=7)

        return cls.query.filter(
            cls.doctor_id == doctor_id,
            cls.date >= start_date,
            cls.date < end_date
        ).order_by(cls.date).all()

    @classmethod
    def set_availability(cls, doctor_id, availability_date, morning_start=None, morning_end=None,
                         evening_start=None, evening_end=None, is_available=True, slot_duration=30):
        """
        Set or update availability for a doctor on a specific date.

        Returns:
            DoctorAvailability instance
        """
        # Validate date is within next 7 days
        today = date.today()
        max_date = today + timedelta(days=7)

        if availability_date < today:
            raise ValueError("Cannot set availability for past dates")
        if availability_date > max_date:
            raise ValueError("Can only set availability for the next 7 days")

        # Find existing or create new
        existing = cls.get_for_doctor_and_date(doctor_id, availability_date)

        if existing:
            existing.start_time_morning = morning_start
            existing.end_time_morning = morning_end
            existing.start_time_evening = evening_start
            existing.end_time_evening = evening_end
            existing.is_available = is_available
            existing.slot_duration = slot_duration
            return existing
        else:
            new_availability = cls(
                doctor_id=doctor_id,
                date=availability_date,
                start_time_morning=morning_start,
                end_time_morning=morning_end,
                start_time_evening=evening_start,
                end_time_evening=evening_end,
                is_available=is_available,
                slot_duration=slot_duration
            )
            db.session.add(new_availability)
            return new_availability
