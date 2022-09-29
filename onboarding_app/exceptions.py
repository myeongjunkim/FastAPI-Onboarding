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
