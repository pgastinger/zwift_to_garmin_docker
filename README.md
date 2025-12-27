- get Garmin MFA token:
```
docker compose run zwift_to_garmin get_mfa_token.py
```

- get Garmin SDK:
-> https://developer.garmin.com/fit/download/


```
cd garmin_sdk
curl https://developer.garmin.com/downloads/fit/sdk/FitSDKRelease_21.188.00.zip -o sdk.zip
unzip sdk.zip
```