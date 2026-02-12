"""
Input validation module for Byte-Sized Business Boost

This module provides comprehensive input validation functions for both
syntactical (format) and semantic (meaning) validation.

VALIDATION PHILOSOPHY:
- Validate early, fail fast
- Provide helpful error messages
- Prevent invalid data from entering the system
- Separate validation logic from business logic

VALIDATION LEVELS:
1. Syntactical: Format checking (e.g., email format, phone format)
2. Semantic: Meaning checking (e.g., rating in valid range, date not in past)
"""

import re
from typing import Tuple, Optional
from datetime import datetime


def validate_business_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate business name input.
    
    Syntactical checks:
    - Not empty
    - Not too long (max 200 characters)
    - Contains at least one letter
    
    Semantic checks:
    - Not just whitespace
    - Not profanity (basic check)
    
    Args:
        name: Business name to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
        - If valid: (True, None)
        - If invalid: (False, error_message)
    
    DESIGN PATTERN: Tuple return for validation
    - Allows for both success/failure and error message
    - More flexible than raising exceptions
    - Caller can decide how to handle errors
    """
    # Syntactical validation: Check if empty or None
    if not name or not isinstance(name, str):
        return False, "Business name is required and must be a string."
    
    # Remove leading/trailing whitespace for validation
    name_trimmed = name.strip()
    
    # Syntactical validation: Check length
    if len(name_trimmed) == 0:
        return False, "Business name cannot be empty or only whitespace."
    
    if len(name_trimmed) > 200:
        return False, "Business name is too long (maximum 200 characters)."
    
    # Semantic validation: Must contain at least one letter
    # This prevents names like "123" or "!!!"
    if not re.search(r'[a-zA-Z]', name_trimmed):
        return False, "Business name must contain at least one letter."
    
    # Basic profanity filter (simple word list - can be expanded)
    # This is semantic validation - checking meaning, not format
    profanity_words = ['spam', 'test', 'fake']  # Add more as needed
    name_lower = name_trimmed.lower()
    for word in profanity_words:
        if word in name_lower:
            return False, f"Business name contains inappropriate content."
    
    return True, None


def validate_category(category: str) -> Tuple[bool, Optional[str]]:
    """
    Validate business category.
    
    Syntactical checks:
    - Not empty
    - Is a string
    
    Semantic checks:
    - Must be one of: 'food', 'retail', 'services'
    
    Args:
        category: Category to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not category or not isinstance(category, str):
        return False, "Category is required and must be a string."
    
    category_lower = category.lower().strip()
    valid_categories = ['food', 'retail', 'services']
    
    # Semantic validation: Must be valid category
    if category_lower not in valid_categories:
        return False, f"Category must be one of: {', '.join(valid_categories)}"
    
    return True, None


def validate_address(address: str) -> Tuple[bool, Optional[str]]:
    """
    Validate business address.
    
    Syntactical checks:
    - Not empty
    - Minimum length (at least 10 characters)
    - Maximum length (max 500 characters)
    
    Semantic checks:
    - Contains street information (number or street name)
    - Not just city/state
    
    Args:
        address: Address to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not address or not isinstance(address, str):
        return False, "Address is required and must be a string."
    
    address_trimmed = address.strip()
    
    if len(address_trimmed) < 10:
        return False, "Address is too short. Please include street address."
    
    if len(address_trimmed) > 500:
        return False, "Address is too long (maximum 500 characters)."
    
    # Semantic validation: Should contain street number or street name
    # Basic check for address-like content
    has_street_number = bool(re.search(r'\d+', address_trimmed))
    has_street_name = bool(re.search(r'\b(street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln|way|circle|cir)\b', address_trimmed, re.IGNORECASE))
    
    if not (has_street_number or has_street_name):
        return False, "Address should include street number or street name."
    
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format.
    
    Syntactical checks:
    - Format: (XXX) XXX-XXXX or XXX-XXX-XXXX or XXX.XXX.XXXX
    - Contains only digits, parentheses, dashes, dots, spaces
    
    Semantic checks:
    - Has correct number of digits (10 for US format)
    
    Args:
        phone: Phone number to validate (optional - empty string is valid)
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Phone is optional - empty string is valid
    if not phone:
        return True, None
    
    if not isinstance(phone, str):
        return False, "Phone number must be a string."
    
    phone_trimmed = phone.strip()
    
    # Remove common formatting characters for validation
    digits_only = re.sub(r'[^\d]', '', phone_trimmed)
    
    # Syntactical validation: Check digit count
    if len(digits_only) < 10:
        return False, "Phone number must contain at least 10 digits."
    
    if len(digits_only) > 15:  # International format max
        return False, "Phone number is too long (maximum 15 digits)."
    
    # Syntactical validation: Check format (US format preferred)
    # Accepts: (XXX) XXX-XXXX, XXX-XXX-XXXX, XXX.XXX.XXXX, XXXXXXXXXX
    phone_pattern = r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
    if not re.match(phone_pattern, phone_trimmed):
        return False, "Phone number format is invalid. Use format: (XXX) XXX-XXXX"
    
    return True, None


def validate_rating(rating: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validate rating value.
    
    Syntactical checks:
    - Can be converted to integer
    
    Semantic checks:
    - Must be between 1 and 5
    
    Args:
        rating: Rating value as string (from form input)
    
    Returns:
        Tuple[bool, Optional[int], Optional[str]]: (is_valid, rating_int, error_message)
        - If valid: (True, rating_int, None)
        - If invalid: (False, None, error_message)
    """
    if not rating:
        return False, None, "Rating is required."
    
    # Syntactical validation: Must be numeric
    try:
        rating_int = int(rating)
    except ValueError:
        return False, None, "Rating must be a number."
    
    # Semantic validation: Must be in valid range
    if not 1 <= rating_int <= 5:
        return False, None, "Rating must be between 1 and 5."
    
    return True, rating_int, None


def validate_comment(comment: str, min_length: int = 3, max_length: int = 1000) -> Tuple[bool, Optional[str]]:
    """
    Validate review comment text.
    
    Syntactical checks:
    - Not empty
    - Length within bounds
    
    Semantic checks:
    - Not just whitespace
    - Contains meaningful content
    
    Args:
        comment: Comment text to validate
        min_length: Minimum character length
        max_length: Maximum character length
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not comment or not isinstance(comment, str):
        return False, "Comment is required and must be a string."
    
    comment_trimmed = comment.strip()
    
    # Syntactical validation: Length check
    if len(comment_trimmed) < min_length:
        return False, f"Comment is too short (minimum {min_length} characters)."
    
    if len(comment_trimmed) > max_length:
        return False, f"Comment is too long (maximum {max_length} characters)."
    
    # Semantic validation: Not just repeated characters
    if len(set(comment_trimmed)) < 3:
        return False, "Comment must contain meaningful content."
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username input.
    
    Syntactical checks:
    - Not empty
    - Length within bounds (2-50 characters)
    - Contains only alphanumeric and spaces
    
    Semantic checks:
    - Not just numbers
    - Not profanity
    
    Args:
        username: Username to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not username or not isinstance(username, str):
        return False, "Username is required and must be a string."
    
    username_trimmed = username.strip()
    
    # Syntactical validation: Length check
    if len(username_trimmed) < 2:
        return False, "Username must be at least 2 characters long."
    
    if len(username_trimmed) > 50:
        return False, "Username is too long (maximum 50 characters)."
    
    # Syntactical validation: Character set check
    # Allow letters, numbers, spaces, and common punctuation
    if not re.match(r'^[a-zA-Z0-9\s\-\'\.]+$', username_trimmed):
        return False, "Username can only contain letters, numbers, spaces, and basic punctuation."
    
    # Semantic validation: Must contain at least one letter
    if not re.search(r'[a-zA-Z]', username_trimmed):
        return False, "Username must contain at least one letter."
    
    return True, None


def validate_deal_title(title: str) -> Tuple[bool, Optional[str]]:
    """
    Validate deal/coupon title.
    
    Args:
        title: Deal title to validate (optional - empty is valid)
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Deal title is optional
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
    """
    Validate date string format and meaning.
    
    Syntactical checks:
    - Format: YYYY-MM-DD
    
    Semantic checks:
    - Is a valid date
    - Not in past (if allow_past=False)
    
    Args:
        date_string: Date string to validate
        allow_past: Whether to allow past dates
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not date_string:
        return True, None  # Date is optional
    
    if not isinstance(date_string, str):
        return False, "Date must be a string."
    
    # Syntactical validation: Format check
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, date_string):
        return False, "Date must be in format YYYY-MM-DD."
    
    # Semantic validation: Is it a valid date?
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        return False, "Date is invalid (e.g., February 30th doesn't exist)."
    
    # Semantic validation: Check if in past
    if not allow_past and date_obj < datetime.now().date():
        return False, "Date cannot be in the past."
    
    return True, None


def validate_verification_answer(user_answer: str, correct_answer: int) -> Tuple[bool, Optional[str]]:
    """
    Validate bot verification answer.
    
    Syntactical checks:
    - Can be converted to integer
    
    Semantic checks:
    - Matches correct answer
    
    Args:
        user_answer: User's answer as string
        correct_answer: Correct answer as integer
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not user_answer:
        return False, "Verification answer is required."
    
    # Syntactical validation: Must be numeric
    try:
        user_answer_int = int(user_answer.strip())
    except ValueError:
        return False, "Verification answer must be a number."
    
    # Semantic validation: Must match correct answer
    if user_answer_int != correct_answer:
        return False, "Verification answer is incorrect. Please try again."
    
    return True, None
