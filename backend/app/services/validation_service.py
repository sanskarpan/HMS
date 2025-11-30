"""
Validation helpers for API input. Sanitizes and validates request data.
"""
import re
import logging
from datetime import datetime, date
from functools import wraps
from flask import request, jsonify
from typing import Dict, Any, List, Tuple, Optional, Callable

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails."""
    def __init__(self, errors: List[str], field: str = None):
        self.errors = errors if isinstance(errors, list) else [errors]
        self.field = field
        super().__init__(str(errors))


class Validator:
    """Common validation methods and patterns."""

    # Regex patterns
    PATTERNS = {
        'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        'username': re.compile(r'^[a-zA-Z0-9_]{3,50}$'),
        'phone': re.compile(r'^[\d\s\-+()]{7,20}$'),
        'name': re.compile(r'^[a-zA-Z\s\'-]{2,100}$'),
        'time': re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'),
        'date': re.compile(r'^\d{4}-\d{2}-\d{2}$'),
        'alphanumeric': re.compile(r'^[a-zA-Z0-9]+$'),
        'safe_text': re.compile(r'^[a-zA-Z0-9\s\.,!?\'"-]+$'),
    }

    # Length limits
    LENGTHS = {
        'username': (3, 50),
        'password': (6, 128),
        'email': (5, 120),
        'phone': (7, 20),
        'name': (2, 100),
        'bio': (0, 2000),
        'text': (0, 5000),
        'short_text': (0, 255),
    }

    @staticmethod
    def sanitize(value: Any) -> Any:
        """Escape HTML chars and strip whitespace."""
        if value is None:
            return None
        if isinstance(value, str):
            # Strip leading/trailing whitespace
            value = value.strip()
            # Remove null bytes
            value = value.replace('\x00', '')
            # Escape HTML special characters
            value = (value
                     .replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;')
                     .replace('"', '&quot;')
                     .replace("'", '&#x27;'))
            return value
        if isinstance(value, dict):
            return {k: Validator.sanitize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [Validator.sanitize(item) for item in value]
        return value

    @staticmethod
    def validate_required(value: Any, field_name: str) -> Tuple[bool, str]:
        """Check if field is present."""
        if value is None:
            return False, f'{field_name} is required'
        if isinstance(value, str) and not value.strip():
            return False, f'{field_name} is required'
        return True, ''

    @staticmethod
    def validate_length(value: str, field_name: str, min_len: int = None, max_len: int = None) -> Tuple[bool, str]:
        """Check string length bounds."""
        if value is None:
            return True, ''
        length = len(value)
        if min_len is not None and length < min_len:
            return False, f'{field_name} must be at least {min_len} characters'
        if max_len is not None and length > max_len:
            return False, f'{field_name} must be at most {max_len} characters'
        return True, ''

    @staticmethod
    def validate_pattern(value: str, pattern_name: str, field_name: str) -> Tuple[bool, str]:
        """Match value against regex."""
        if value is None:
            return True, ''
        pattern = Validator.PATTERNS.get(pattern_name)
        if pattern and not pattern.match(value):
            return False, f'{field_name} format is invalid'
        return True, ''

    @staticmethod
    def validate_email(email: str, required: bool = True) -> Tuple[bool, str]:
        """Check email format."""
        if not email and not required:
            return True, ''
        valid, msg = Validator.validate_required(email, 'Email')
        if not valid:
            return valid, msg
        valid, msg = Validator.validate_length(email, 'Email', *Validator.LENGTHS['email'])
        if not valid:
            return valid, msg
        return Validator.validate_pattern(email.lower(), 'email', 'Email')

    @staticmethod
    def validate_username(username: str, required: bool = True) -> Tuple[bool, str]:
        """Check username format and length."""
        if not username and not required:
            return True, ''
        valid, msg = Validator.validate_required(username, 'Username')
        if not valid:
            return valid, msg
        valid, msg = Validator.validate_length(username, 'Username', *Validator.LENGTHS['username'])
        if not valid:
            return valid, msg
        return Validator.validate_pattern(username, 'username', 'Username')

    @staticmethod
    def validate_password(password: str, required: bool = True) -> Tuple[bool, str]:
        """Check password length."""
        if not password and not required:
            return True, ''
        valid, msg = Validator.validate_required(password, 'Password')
        if not valid:
            return valid, msg
        return Validator.validate_length(password, 'Password', *Validator.LENGTHS['password'])

    @staticmethod
    def validate_phone(phone: str, required: bool = False) -> Tuple[bool, str]:
        """Check phone format."""
        if not phone and not required:
            return True, ''
        if not phone and required:
            return False, 'Phone number is required'
        return Validator.validate_pattern(phone, 'phone', 'Phone number')

    @staticmethod
    def validate_name(name: str, field_name: str = 'Name', required: bool = True) -> Tuple[bool, str]:
        """Check name format."""
        if not name and not required:
            return True, ''
        valid, msg = Validator.validate_required(name, field_name)
        if not valid:
            return valid, msg
        valid, msg = Validator.validate_length(name, field_name, *Validator.LENGTHS['name'])
        if not valid:
            return valid, msg
        return Validator.validate_pattern(name, 'name', field_name)

    @staticmethod
    def validate_date(date_str: str, field_name: str = 'Date', required: bool = True,
                      min_date: date = None, max_date: date = None) -> Tuple[bool, str]:
        """Check date in YYYY-MM-DD format."""
        if not date_str and not required:
            return True, ''
        if not date_str and required:
            return False, f'{field_name} is required'

        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return False, f'{field_name} must be in YYYY-MM-DD format'

        if min_date and parsed_date < min_date:
            return False, f'{field_name} cannot be before {min_date.isoformat()}'
        if max_date and parsed_date > max_date:
            return False, f'{field_name} cannot be after {max_date.isoformat()}'

        return True, ''

    @staticmethod
    def validate_time(time_str: str, field_name: str = 'Time', required: bool = True) -> Tuple[bool, str]:
        """Check time in HH:MM format."""
        if not time_str and not required:
            return True, ''
        if not time_str and required:
            return False, f'{field_name} is required'
        return Validator.validate_pattern(time_str, 'time', field_name)

    @staticmethod
    def validate_integer(value: Any, field_name: str, required: bool = True,
                         min_val: int = None, max_val: int = None) -> Tuple[bool, str]:
        """Check integer and bounds."""
        if value is None and not required:
            return True, ''
        if value is None and required:
            return False, f'{field_name} is required'

        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, f'{field_name} must be an integer'

        if min_val is not None and int_value < min_val:
            return False, f'{field_name} must be at least {min_val}'
        if max_val is not None and int_value > max_val:
            return False, f'{field_name} must be at most {max_val}'

        return True, ''

    @staticmethod
    def validate_float(value: Any, field_name: str, required: bool = True,
                       min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
        """Check float and bounds."""
        if value is None and not required:
            return True, ''
        if value is None and required:
            return False, f'{field_name} is required'

        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return False, f'{field_name} must be a number'

        if min_val is not None and float_value < min_val:
            return False, f'{field_name} must be at least {min_val}'
        if max_val is not None and float_value > max_val:
            return False, f'{field_name} must be at most {max_val}'

        return True, ''

    @staticmethod
    def validate_enum(value: str, allowed_values: List[str], field_name: str,
                      required: bool = True) -> Tuple[bool, str]:
        """Check value is one of allowed options."""
        if not value and not required:
            return True, ''
        if not value and required:
            return False, f'{field_name} is required'
        if value not in allowed_values:
            return False, f'{field_name} must be one of: {", ".join(allowed_values)}'
        return True, ''


class SchemaValidator:
    """Validates dict data against a schema definition."""

    def __init__(self):
        self.errors: List[str] = {}

    def validate(self, data: Dict[str, Any], schema: Dict[str, Dict]) -> Tuple[bool, Dict[str, str]]:
        """Run all field validations defined in schema. Returns (is_valid, errors)."""
        errors = {}

        for field_name, rules in schema.items():
            value = data.get(field_name)
            required = rules.get('required', True)
            field_type = rules.get('type', 'string')

            # Type-specific validation
            if field_type == 'email':
                valid, msg = Validator.validate_email(value, required)
            elif field_type == 'username':
                valid, msg = Validator.validate_username(value, required)
            elif field_type == 'password':
                valid, msg = Validator.validate_password(value, required)
            elif field_type == 'phone':
                valid, msg = Validator.validate_phone(value, required)
            elif field_type == 'name':
                valid, msg = Validator.validate_name(value, field_name, required)
            elif field_type == 'date':
                min_date = rules.get('min_date')
                max_date = rules.get('max_date')
                valid, msg = Validator.validate_date(value, field_name, required, min_date, max_date)
            elif field_type == 'time':
                valid, msg = Validator.validate_time(value, field_name, required)
            elif field_type == 'integer':
                min_val = rules.get('min')
                max_val = rules.get('max')
                valid, msg = Validator.validate_integer(value, field_name, required, min_val, max_val)
            elif field_type == 'float':
                min_val = rules.get('min')
                max_val = rules.get('max')
                valid, msg = Validator.validate_float(value, field_name, required, min_val, max_val)
            elif field_type == 'enum':
                allowed_values = rules.get('values', [])
                valid, msg = Validator.validate_enum(value, allowed_values, field_name, required)
            else:
                # Default string validation
                if not value and not required:
                    valid, msg = True, ''
                elif not value and required:
                    valid, msg = False, f'{field_name} is required'
                else:
                    min_len = rules.get('min_length')
                    max_len = rules.get('max_length')
                    valid, msg = Validator.validate_length(value, field_name, min_len, max_len)

            if not valid:
                errors[field_name] = msg

            # Custom validation
            if valid and 'custom' in rules and value:
                custom_result = rules['custom'](value, data)
                if isinstance(custom_result, tuple):
                    custom_valid, custom_msg = custom_result
                else:
                    custom_valid, custom_msg = custom_result, f'{field_name} is invalid'
                if not custom_valid:
                    errors[field_name] = custom_msg

        return len(errors) == 0, errors


# Predefined schemas for common data types
SCHEMAS = {
    'login': {
        'username': {'type': 'string', 'required': True, 'min_length': 1},
        'password': {'type': 'string', 'required': True, 'min_length': 1}
    },
    'register': {
        'username': {'type': 'username', 'required': True},
        'email': {'type': 'email', 'required': True},
        'password': {'type': 'password', 'required': True},
        'full_name': {'type': 'name', 'required': True},
        'phone': {'type': 'phone', 'required': True}
    },
    'doctor': {
        'full_name': {'type': 'name', 'required': True},
        'department_id': {'type': 'integer', 'required': True, 'min': 1},
        'qualification': {'type': 'string', 'required': False, 'max_length': 255},
        'experience_years': {'type': 'integer', 'required': False, 'min': 0, 'max': 70},
        'phone': {'type': 'phone', 'required': False},
        'bio': {'type': 'string', 'required': False, 'max_length': 2000},
        'consultation_fee': {'type': 'float', 'required': False, 'min': 0, 'max': 10000}
    },
    'appointment': {
        'doctor_id': {'type': 'integer', 'required': True, 'min': 1},
        'appointment_date': {'type': 'date', 'required': True},
        'appointment_time': {'type': 'time', 'required': True},
        'reason': {'type': 'string', 'required': False, 'max_length': 500}
    },
    'treatment': {
        'appointment_id': {'type': 'integer', 'required': True, 'min': 1},
        'diagnosis': {'type': 'string', 'required': True, 'min_length': 1, 'max_length': 2000},
        'prescription': {'type': 'string', 'required': False, 'max_length': 2000},
        'notes': {'type': 'string', 'required': False, 'max_length': 2000},
        'tests_recommended': {'type': 'string', 'required': False, 'max_length': 2000},
        'visit_type': {'type': 'enum', 'required': False, 'values': ['in-person', 'follow-up', 'emergency']}
    }
}


def validate_request(schema_name: str = None, schema: Dict = None):
    """Decorator that validates JSON body before calling the route handler."""
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json() or {}

            # Get schema
            validation_schema = schema or SCHEMAS.get(schema_name, {})

            if not validation_schema:
                return f(*args, **kwargs)

            # Sanitize input
            sanitized_data = Validator.sanitize(data)

            # Validate
            validator = SchemaValidator()
            is_valid, errors = validator.validate(sanitized_data, validation_schema)

            if not is_valid:
                logger.warning(f'Validation failed for {f.__name__}: {errors}')
                return jsonify({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': errors
                }), 400

            # Store sanitized data in request for use in endpoint
            request.validated_data = sanitized_data
            return f(*args, **kwargs)

        return decorated_function
    return decorator


# Direct validation without decorator
def validate_data(data: Dict, schema_name: str = None, schema: Dict = None) -> Tuple[bool, Dict]:
    """Validate dict against schema. Returns (is_valid, errors)."""
    validation_schema = schema or SCHEMAS.get(schema_name, {})
    if not validation_schema:
        return True, {}

    sanitized_data = Validator.sanitize(data)
    validator = SchemaValidator()
    return validator.validate(sanitized_data, validation_schema)
