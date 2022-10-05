class OnboardingException(Exception):
    ...


class DataDoesNotExistError(OnboardingException):
    ...


class UserDuplicatedError(OnboardingException):
    ...


class CredentialsError(OnboardingException):
    ...


class InactiveUserError(OnboardingException):
    ...


class FileOpenError(OnboardingException):
    ...
