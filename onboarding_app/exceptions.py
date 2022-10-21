class OnboardingException(Exception):
    ...


class DataDoesNotExistError(OnboardingException):
    ...


class DuplicatedError(OnboardingException):
    ...


class CredentialsError(OnboardingException):
    ...


class InactiveUserError(OnboardingException):
    ...


class FileOpenError(OnboardingException):
    ...


class PermissionDeniedError(OnboardingException):
    ...


class InvalidQueryError(OnboardingException):
    ...


class StockNotFoundError(OnboardingException):
    ...
