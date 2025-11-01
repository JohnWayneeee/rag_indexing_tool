"""
Entry point for running FastAPI server
"""
import sys
from pathlib import Path

# Add project root to PYTHONPATH
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import uvicorn
from src.config.settings import API_HOST, API_PORT, API_RELOAD
from src.api.routes import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )

