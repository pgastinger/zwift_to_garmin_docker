"""Zwift service for handling authentication and activity downloads."""

import os
import tempfile
import requests
import logging
from typing import Optional, Dict, Any
from zwift import Client as ZwiftClient
from datetime import datetime, timezone

class ZwiftService:
    """Service for interacting with Zwift API."""

    def __init__(self, username: str, password: str):
        """Initialize ZwiftService with credentials.

        Args:
            username: Zwift username
            password: Zwift password
        """
        self.username = username
        self.password = password
        self.client: Optional[ZwiftClient] = None
        self.logger = logging.getLogger(__name__)
        # Save the .fit file to a temporary location
        self.temp_dir = tempfile.gettempdir()        

    def authenticate(self) -> None:
        """Authenticate with Zwift."""
        self.logger.info("Authenticating with Zwift...")
        self.client = ZwiftClient(self.username, self.password)
        self.logger.info("Successfully authenticated with Zwift")


    def _get_activities(self) -> []:
        if not self.client:
            raise RuntimeError("Must authenticate before downloading activities")

        profile = self.client.get_profile()
        start = 0
        limit = 10
        activities = []
        while True:
            act = profile.get_activities(start, limit)
            activities.extend(act)
            start += limit
            if len(act) != limit:
                break

        self.logger.info(f"Activities found: {len(activities)}")

        if len(activities) == 0:
            self.logger.info("No activities found on Zwift")
            return None
        return activities
    

    def download_last_activity(self) -> Optional[str]:
        """Downloads the last activity's .fit file from Zwift.

        Returns:
            Path to downloaded .fit file, or None if no activities found

        Raises:
            RuntimeError: If not authenticated or download fails
        """

        activities = self._get_activities()
        return self.download_activity(activities[0])


    def download_activity(self, activity):
        activity_id = activity['id']
        self.logger.info(f"Downloading activity {activity_id}...")

        link = f"https://{activity['fitFileBucket']}.s3.amazonaws.com/{activity['fitFileKey']}"
        self.logger.info(f"Download link: {link}")

        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download activity: {e}") from e


        fit_file_path = os.path.join(self.temp_dir, f"zwift_activity_{activity_id}.fit")

        with open(fit_file_path, "wb") as file:
            file.write(response.content)

        self.logger.info(f"Activity {activity_id} downloaded to {fit_file_path}")
        return fit_file_path


    def download_last_x_activities(self, x: int) -> Optional[str]:
        activities = self._get_activities()
        fit_file_path_list = []
        for i in range(0,x):
            self.logger.info(f"Download activitiy {i}")
            fit_file_path_list.append(self.download_activity(activities[i]))
        return fit_file_path_list


    def download_activities_since_date(self, start_date: str) -> Optional[str]:
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        activities = self._get_activities()
        fit_file_path_list = []
        for i, activity in enumerate(activities):
            activity_start_date_dt = datetime.strptime(activity["startDate"], "%Y-%m-%dT%H:%M:%S.%f%z")
            self.logger.info(f"Check activity with start_date {activity_start_date_dt}")
            if start_date_dt < activity_start_date_dt.replace(tzinfo=None):
                self.logger.info(f"Download activitiy {i}")
                print(f"Download activitiy {i}: {activity_start_date_dt}")
                fit_file_path_list.append(self.download_activity(activity))
        return fit_file_path_list

