
from app.utils.HttpResponseUtils import response_format
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from config.setting import env
import logging

logger = logging.getLogger(__name__)

def setup_exception(app):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        detail = exc.detail if isinstance(exc.detail, dict) else { "msg": None, "data": None }
        return response_format(detail.get('msg'),exc.status_code, detail.get('data'))


    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.warning(f"Validation error: {str(exc)}")
        return response_format("Terjadi kesalahan, silahkan coba lagi",400, str(exc))
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        # Log the full exception with traceback
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        # Check if we're in debug mode using APP_ENV from settings
        is_debug = env.APP_ENV.lower() == "development"
        error_detail = {"error": str(exc)} if is_debug else None
        return response_format(
            "Terjadi kesalahan internal server", 
            500, 
            error_detail
        )

