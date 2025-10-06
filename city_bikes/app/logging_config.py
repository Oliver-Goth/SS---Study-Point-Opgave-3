from loguru import logger
import uuid
import contextvars
import json
from datetime import datetime

correlation_id_var = contextvars.ContextVar("correlation_id", default=None)

# til at lave audit.log filen med 90 dags retention og rotation hver dag ved midnat  
logger.add(
    "logs/audit.log",
    rotation="00:00",
    retention="90 days",
    serialize=True,
    level="INFO",
    filter=lambda record: record["extra"].get("log_type") == "audit",
)

# Standard log format for console and general log file
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{extra[correlation_id]}</cyan> | <level>{message}</level>",
    level="DEBUG",
)

#Til at lave en app.log fil med 14 dags retention og rotation hver dag ved midnat
logger.add(
    "logs/app.log",
    rotation="00:00",
    retention="14 days",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[correlation_id]} | {message}",
    level="DEBUG",
)


def audit_log(action,user_id,resource_id=None,ip=None):
    correlation_id = get_correlation_id()
    logger.bind(
        correlation_id=correlation_id,
        log_type="audit",
    ).info(
        {
            "@timestamp": datetime.utcnow().isoformat() + "Z",
            "level": "INFO",
            "logger_name": "AUDIT",
            "message": "USER_ACTION",
            "action": action,
            "user_id": user_id,
            "resource_id": resource_id,
            "ip": ip,
            "correlation_id": correlation_id,
            "log_type": "audit",
            "service": "city-bikes"
        }
    )

def get_correlation_id():
    return correlation_id_var.get() or "no-correlation-id"

def set_correlation_id(correlation_id=None):
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id


def handle_reservation(user_id, bike_id, ip):
    

    correlation_id = set_correlation_id()
    bound_logger = logger.bind(correlation_id=correlation_id)

    bound_logger.info("Handling reservation started")

    audit_log("reservation_created", user_id, bike_id, ip)

    logger.info("Reservation finished")