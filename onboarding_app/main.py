from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from onboarding_app import exceptions
from onboarding_app.database import Base, engine
from onboarding_app.endpoints.stock import stock_router
from onboarding_app.endpoints.user import user_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user_router)
app.include_router(stock_router)


@app.exception_handler(exceptions.CredentialsError)
async def credentialsError_exception_handler(
    request: Request, exc: exceptions.CredentialsError
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(exceptions.DuplicatedError)
async def duplicated_exception_handler(
    request: Request, exc: exceptions.DuplicatedError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content="Data info is duplicated",
    )


@app.exception_handler(exceptions.DataDoesNotExistError)
async def data_does_not_exist_exception_handler(
    request: Request, exc: exceptions.DataDoesNotExistError
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content="Data not found",
    )


@app.exception_handler(exceptions.InactiveUserError)
async def inactive_user_exception_handler(
    request: Request, exc: exceptions.InactiveUserError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content="Inactive user",
    )
