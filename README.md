# SS---Study-Point-Opgave-3

## How to run
- create a virtual environment
  - python -m venv venv
  - .\venv\Scripts\activate
- pip install -r requirements.txt
- python main.py

Then test in Postman or similar

## Logging
We log debug, info, error and warnings, here are some examples of uses in the code:
- Debug: logger.add(...level="DEBUG",)
- Info: bound_logger.info("Attempting to reserve bike")
- Warning: bound_logger.warning(f"Unauthorized admin {admin_id}")
- Error: bound_logger.error(f"Bike {bike_id} not found")

## Rotation and retention
In our project, log rotation and log retention are configured in the logging_config file, using Loguru.
| Log Type         | File Path        | Rotation Time        | Retention Period | Format Type       | Purpose                                          |
|------------------|------------------|-----------------------|------------------|-------------------|--------------------------------------------------|
| **Audit Log**     | `logs/audit.log` | Every midnight (`00:00`) | 90 days          | JSON (serialized) | Track user actions (e.g. login, reservations)   |
| **Application Log** | `logs/app.log`  | Every midnight (`00:00`) | 14 days          | Plain text        | General debug/info logging                      |
