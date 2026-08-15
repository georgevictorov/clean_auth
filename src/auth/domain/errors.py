class DomainError(Exception):
    """Base class for domain errors."""
    ...


class InfrastructureError(Exception):
    """Infrastructure failure."""
    ...


# Validation

class ValidationError(DomainError):
    """Invalid domain value."""
    ...


class InvalidUsername(ValidationError):
    ...


class InvalidUserID(ValidationError):
    ...


class InvalidPasswordHash(ValidationError):
    ...


class InvalidExpirationTime(ValidationError):
    ...


class InvalidCreationTime(ValidationError):
    ...


# Authentication

class TokenDecodeError(DomainError):
    """Token cannot be decoded or validated."""
    ...


class InvalidCredentials(DomainError):
    """Provided credentials are invalid."""
    ...


# User

class UserAlreadyExists(DomainError):
    ...


class UserNotFound(DomainError):
    ...


# Concurrency

class ConflictError(DomainError):
    """Domain conflict."""
    ...


class ConcurrencyError(ConflictError):
    ...