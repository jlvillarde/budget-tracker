from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f'Uncaught exception: {exc}', exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error occurred."},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []

    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_type = error.get("type", "validation_error")
        input_value = error.get("input", "N/A")

        formatted_errors.append({
            "field": field_path,
            "message": message,
            "type": error_type,
            "invalid_value": input_value,
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": formatted_errors,
            "hint": "Ensure all fields have correct values based on the expected format."
        },
    )
