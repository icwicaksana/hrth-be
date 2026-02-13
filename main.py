import uvicorn
import logging
from app.Kernel import app
from config.middleware import setup_middleware
from config.routes import setup_routes
from config.exception import setup_exception

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

setup_middleware(app)
setup_exception(app)
setup_routes(app)

if __name__ == "__main__":
    uvicorn.run("main:app",
            host="0.0.0.0",
            port=8001,
            reload=True
            )
