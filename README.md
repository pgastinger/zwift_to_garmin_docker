- get Garmin MFA token:
```
docker compose run zwift_to_garmin get_mfa_token.py
```

- get Garmin SDK
-> https://developer.garmin.com/fit/download/

- test
```
peter@pptm-linux:~/vscode/zwift-to-garmin-docker$ docker compose run zwift_to_garmin test_java_lib.py
WARN[0000] Found orphan containers ([zwift-to-garmin-docker-zwift_to_garmin-run-fd404ff075e0]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up. 
Container zwift-to-garmin-docker-zwift_to_garmin-run-8ad06b0453df Creating 
Container zwift-to-garmin-docker-zwift_to_garmin-run-8ad06b0453df Created 
<java class 'com.garmin.fit.csv.CSVTool'>
```

- run as job to sync latest activity to garmin
```
peter@pptm-linux:~/vscode/zwift-to-garmin-docker$ docker compose run zwift_to_garmin
```
