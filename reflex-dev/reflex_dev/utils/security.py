"""Security utilities for password hashing and verification."""

import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    # Generate a random salt
    salt = secrets.token_hex(16)
    
    # Create hash with salt
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Return salt + hash
    return f"{salt}${password_hash}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        # Split salt and hash
        salt, stored_hash = hashed_password.split('$')
        
        # Hash the provided password with the stored salt
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        # Compare hashes
        return password_hash == stored_hash
    except ValueError:
        # Invalid hash format
        return False
