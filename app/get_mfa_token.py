import garth
import os

garmin_username = os.getenv("GARMIN_USERNAME")
garmin_password = os.getenv("GARMIN_PASSWORD")
# If MFA is enabled, you'll be prompted for the code here
garth.login(garmin_username, garmin_password)

# Save the session tokens for future use (up to one year)
garth.save("/app/data/.garth")
