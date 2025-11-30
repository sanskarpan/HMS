from . import db, TimestampMixin


class Department(db.Model, TimestampMixin):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    doctors = db.relationship('Doctor', back_populates='department', lazy='dynamic')
    appointments = db.relationship('Appointment', back_populates='department', lazy='dynamic')

    def __init__(self, name, description=None):
        """Initialize a new department."""
        self.name = name
        self.description = description

    @property
    def doctors_count(self):
        """Get the count of active doctors in this department."""
        return self.doctors.filter_by(is_active=True).count()

    @property
    def active_doctors(self):
        """Get list of active doctors in this department."""
        return self.doctors.filter_by(is_active=True).all()

    def to_dict(self, include_doctors=False):
        """Convert department to dictionary representation."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'doctors_count': self.doctors_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_doctors:
            data['doctors'] = [doc.to_dict() for doc in self.active_doctors]

        return data

    def __repr__(self):
        return f'<Department {self.name}>'

    @classmethod
    def find_by_name(cls, name):
        """Find department by name (case-insensitive)."""
        return cls.query.filter(cls.name.ilike(name)).first()

    @classmethod
    def get_all_active(cls):
        """Get all active departments."""
        return cls.query.filter_by(is_active=True).order_by(cls.name).all()

    @classmethod
    def search(cls, query):
        """Search departments by name or description."""
        search_term = f'%{query}%'
        return cls.query.filter(
            cls.is_active == True,
            (cls.name.ilike(search_term) | cls.description.ilike(search_term))
        ).order_by(cls.name).all()


# Default departments to seed
DEFAULT_DEPARTMENTS = [
    {
        'name': 'Cardiology',
        'description': 'Specializes in diagnosing and treating diseases of the heart and blood vessels, including heart attacks, arrhythmias, and heart failure.'
    },
    {
        'name': 'Oncology',
        'description': 'Dedicated to the diagnosis, treatment, and care of patients with cancer, including medical oncology, surgical oncology, and radiation oncology.'
    },
    {
        'name': 'General Medicine',
        'description': 'Primary care for adults, treating common illnesses and chronic conditions.'
    },
    {
        'name': 'Orthopedics',
        'description': 'Focuses on the diagnosis and treatment of disorders of the bones, joints, muscles, ligaments, and tendons.'
    },
    {
        'name': 'Pediatrics',
        'description': 'Specializes in medical care for infants, children, and adolescents, from birth through age 18.'
    },
    {
        'name': 'Dermatology',
        'description': 'Deals with diseases of the skin, hair, and nails, including conditions like acne, eczema, psoriasis, and skin cancer.'
    },
    {
        'name': 'Neurology',
        'description': 'Specializes in disorders of the nervous system, including the brain, spinal cord, and peripheral nerves.'
    },
    {
        'name': 'Psychiatry',
        'description': 'Focuses on the diagnosis, treatment, and prevention of mental, emotional, and behavioral disorders.'
    },
    {
        'name': 'Gynecology',
        'description': 'Specializes in women\'s reproductive health, including pregnancy, childbirth, and disorders of the reproductive system.'
    },
    {
        'name': 'Ophthalmology',
        'description': 'Deals with the diagnosis and treatment of eye disorders, including vision problems, cataracts, and glaucoma.'
    }
]
