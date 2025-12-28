"""Main entry point for Zwift to Garmin activity transfer."""

import sys
import os
import logging
import uvicorn

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from services.zwift_service import ZwiftService
from services.fit_file_service import FitFileService
from services.garmin_service import GarminService
from services.activity_processor import ActivityProcessor

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.get("/sync_latest/")
def sync_latest():
    """Main function to orchestrate the activity transfer process."""
    # Load environment variables from .env file
    logger = logging.getLogger(__name__)
    logger.info("test")
    garmin_username = os.getenv("GARMIN_USERNAME")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    zwift_username = os.getenv("ZWIFT_USERNAME")
    zwift_password = os.getenv("ZWIFT_PASSWORD")

    # Validate required environment variables
    if not all([zwift_username, zwift_password, garmin_username, garmin_password]):
        raise ValueError("Missing required environment variables.")

    # Initialize services with dependency injection
    zwift_service = ZwiftService(zwift_username, zwift_password)
    fit_file_service = FitFileService()
    garmin_service = GarminService(garmin_username, garmin_password)

    # Create the main processor
    processor = ActivityProcessor(zwift_service, garmin_service, fit_file_service)

    # Process the latest activity
    success = processor.process_latest_activity()

    if success:
        return {"success": "Activity successfully transferred from Zwift to Garmin"}
    else:
        return {"failed": "Failed to transfer activity. Check the logs for details."}  


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/docs")    

# This block tells Python what to do when the script is run directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)