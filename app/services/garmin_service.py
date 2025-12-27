"""Garmin service for handling authentication and activity uploads."""

import logging
from typing import Dict, Any
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
    GarminConnectConnectionError
)

TOKEN_FILE="/app/data/.garth"


class GarminService:
    """Service for interacting with Garmin Connect."""

    def __init__(self, username: str, password: str):
        """Initialize GarminService with credentials.

        Args:
            username: Garmin Connect username
            password: Garmin Connect password
        """
        self.username = username
        self.password = password
        self.client: Garmin = Garmin()
        self.logger = logging.getLogger(__name__)
        self._authenticated = False

    def authenticate(self) -> None:
        """Authenticate with Garmin Connect.

        Raises:
            GarminConnectAuthenticationError: Invalid credentials
            GarminConnectTooManyRequestsError: Rate limit exceeded
            GarminConnectConnectionError: Network connection issues
            RuntimeError: Other authentication failures
        """
        self.logger.info("Logging in to Garmin Connect...")

        try:
            self.client.login(TOKEN_FILE)
            self._authenticated = True
            self.logger.info("Successfully authenticated with Garmin Connect")
        except GarminConnectAuthenticationError:
            self.logger.exception("Authentication error. Check your credentials.")
            raise
        except GarminConnectTooManyRequestsError:
            self.logger.exception("Too many requests. Try again later.")
            raise
        except GarminConnectConnectionError:
            self.logger.exception("Connection error. Check your internet connection.")
            raise
        except Exception as e:
            self.logger.exception(f"Failed to login to Garmin Connect: {e}")
            raise RuntimeError(f"Authentication failed: {e}") from e

    def upload_activity(self, fit_file_path: str) -> Dict[str, Any]:
        """Upload a .fit file to Garmin Connect.

        Args:
            fit_file_path: Path to the FIT file to upload

        Returns:
            Upload response from Garmin Connect

        Raises:
            RuntimeError: If not authenticated or upload fails
        """
        if not self._authenticated:
            raise RuntimeError("Must authenticate before uploading activities")

        self.logger.info(f"Uploading {fit_file_path} to Garmin Connect...")

        try:
            response = self.client.upload_activity(fit_file_path)
            self.logger.info("Upload successful")
            self.logger.debug(f"Upload response: {response}")
            return response
        except Exception as e:
            self.logger.exception(f"Failed to upload activity: {e}")

            if e.error.response.status_code != 409:
                raise RuntimeError(f"Upload failed: {e}") from e

    def is_authenticated(self) -> bool:
        """Check if the service is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated
