
import re
from typing import Tuple, Optional
from datetime import datetime


def validate_business_name(name: str) -> Tuple[bool, Optional[str]]:
    if not name or not isinstance(name, str):
        return False, "Business name is required and must be a string."
    
    name_trimmed = name.strip()
    
    if len(name_trimmed) == 0:
        return False, "Business name cannot be empty or only whitespace."
    
    if len(name_trimmed) > 200:
        return False, "Business name is too long (maximum 200 characters)."
    
    if not re.search(r'[a-zA-Z]', name_trimmed):
        return False, "Business name must contain at least one letter."
    
    profanity_words = ['spam', 'test', 'fake']  # Add more as needed
    name_lower = name_trimmed.lower()
    for word in profanity_words:
        if word in name_lower:
            return False, f"Business name contains inappropriate content."
    
    return True, None


def validate_category(category: str) -> Tuple[bool, Optional[str]]:
    if not category or not isinstance(category, str):
        return False, "Category is required and must be a string."
    
    category_lower = category.lower().strip()
    valid_categories = ['food', 'retail', 'services']
    
    if category_lower not in valid_categories:
        return False, f"Category must be one of: {', '.join(valid_categories)}"
    
    return True, None


def validate_address(address: str) -> Tuple[bool, Optional[str]]:
    if not address or not isinstance(address, str):
        return False, "Address is required and must be a string."
    
    address_trimmed = address.strip()
    
    if len(address_trimmed) < 10:
        return False, "Address is too short. Please include street address."
    
    if len(address_trimmed) > 500:
        return False, "Address is too long (maximum 500 characters)."
    
    has_street_number = bool(re.search(r'\d+', address_trimmed))
    has_street_name = bool(re.search(r'\b(street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln|way|circle|cir)\b', address_trimmed, re.IGNORECASE))
    
    if not (has_street_number or has_street_name):
        return False, "Address should include street number or street name."
    
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    if not phone:
        return True, None
    
    if not isinstance(phone, str):
        return False, "Phone number must be a string."
    
    phone_trimmed = phone.strip()
    
    digits_only = re.sub(r'[^\d]', '', phone_trimmed)
    
    if len(digits_only) < 10:
        return False, "Phone number must contain at least 10 digits."
    
    if len(digits_only) > 15:  # International format max
        return False, "Phone number is too long (maximum 15 digits)."
    
    phone_pattern = r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
    if not re.match(phone_pattern, phone_trimmed):
        return False, "Phone number format is invalid. Use format: (XXX) XXX-XXXX"
    
    return True, None


def validate_rating(rating: str) -> Tuple[bool, Optional[int], Optional[str]]:
    if not rating:
        return False, None, "Rating is required."
    
    try:
        rating_int = int(rating)
    except ValueError:
        return False, None, "Rating must be a number."
    
    if not 1 <= rating_int <= 5:
        return False, None, "Rating must be between 1 and 5."
    
    return True, rating_int, None


def validate_comment(comment: str, min_length: int = 3, max_length: int = 1000) -> Tuple[bool, Optional[str]]:
    if not comment or not isinstance(comment, str):
        return False, "Comment is required and must be a string."
    
    comment_trimmed = comment.strip()
    
    if len(comment_trimmed) < min_length:
        return False, f"Comment is too short (minimum {min_length} characters)."
    
    if len(comment_trimmed) > max_length:
        return False, f"Comment is too long (maximum {max_length} characters)."
    
    if len(set(comment_trimmed)) < 3:
        return False, "Comment must contain meaningful content."
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    if not username or not isinstance(username, str):
        return False, "Username is required and must be a string."
    
    username_trimmed = username.strip()
    
    if len(username_trimmed) < 2:
        return False, "Username must be at least 2 characters long."
    
    if len(username_trimmed) > 50:
        return False, "Username is too long (maximum 50 characters)."
    
    if not re.match(r'^[a-zA-Z0-9\s\-\'\.]+$', username_trimmed):
        return False, "Username can only contain letters, numbers, spaces, and basic punctuation."
    
    if not re.search(r'[a-zA-Z]', username_trimmed):
        return False, "Username must contain at least one letter."
    
    return True, None


def validate_deal_title(title: str) -> Tuple[bool, Optional[str]]:
    if not title:
        return True, None
    
    if not isinstance(title, str):
        return False, "Deal title must be a string."
    
    title_trimmed = title.strip()
    
    if len(title_trimmed) < 3:
        return False, "Deal title must be at least 3 characters long."
    
    if len(title_trimmed) > 100:
        return False, "Deal title is too long (maximum 100 characters)."
    
    return True, None


def validate_date(date_string: str, allow_past: bool = False) -> Tuple[bool, Optional[str]]:
    if not date_string:
        return True, None  # Date is optional
    
    if not isinstance(date_string, str):
        return False, "Date must be a string."
    
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, date_string):
        return False, "Date must be in format YYYY-MM-DD."
    
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        return False, "Date is invalid (e.g., February 30th doesn't exist)."
    
    if not allow_past and date_obj < datetime.now().date():
        return False, "Date cannot be in the past."
    
    return True, None


def validate_verification_answer(user_answer: str, correct_answer: int) -> Tuple[bool, Optional[str]]:
    if not user_answer:
        return False, "Verification answer is required."
    
    try:
        user_answer_int = int(user_answer.strip())
    except ValueError:
        return False, "Verification answer must be a number."
    
    if user_answer_int != correct_answer:
        return False, "Verification answer is incorrect. Please try again."
    
    return True, None
