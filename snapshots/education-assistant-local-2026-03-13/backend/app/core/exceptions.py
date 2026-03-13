from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError):
        first_error = exc.errors()[0] if exc.errors() else None
        if first_error is None:
            detail = "请求参数不合法"
        else:
            location = first_error.get("loc", [])
            field_name = str(location[-1]) if location else "field"
            detail = f"{field_name}: {first_error.get('msg', '请求参数不合法')}"
        return JSONResponse(status_code=422, content={"detail": detail})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, __: Exception):
        return JSONResponse(status_code=500, content={"detail": "服务器内部错误，请稍后重试"})
