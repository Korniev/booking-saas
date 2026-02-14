from app.core.exceptions import ConflictError


class UserAlreadyExistsError(ConflictError):
    pass