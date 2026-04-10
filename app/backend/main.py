import uvicorn
from dotenv import load_dotenv
from src.infrastructure.utils.logger import ColorLogger
from src.presentation.api.main import app


load_dotenv()
logger = ColorLogger("ROOT")


if __name__ == "__main__":
    logger.info("Iniciando motor do Agente...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
