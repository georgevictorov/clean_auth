class DomainError(Exception):
    ...


class ValidationError(DomainError):
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
