from datetime import datetime
import app.logging_config as log_cfg
import app.storage as store
import uuid

def list_bikes():
    correlation_id = log_cfg.set_correlation_id()
    bound_logger = log_cfg.logger.bind(correlation_id=correlation_id)
    bound_logger.info("Fetching bike list")
    available_bikes = [bike for bike in store.bikes.values() if bike["status"] == "available"]
    bound_logger.info(f"Found {len(available_bikes)} available bikes")
    return available_bikes

def reserve_bike(bike_id, user_id, ip="127.0.0.1"):
    correlation_id = log_cfg.set_correlation_id()
    bound_logger = log_cfg.logger.bind(correlation_id=correlation_id)
    bound_logger.info("Attempting to reserve bike")

    bike = store.bikes.get(bike_id)
    if not bike:
        bound_logger.warning(f"Bike {bike_id} not found")
        return None
    if bike["status"] != "available":
        bound_logger.warning(f"Bike {bike_id} is not available")
        return None

    reservation_id = str(uuid.uuid4())
    store.reservations[reservation_id] = {"user_id": user_id, "bike_id": bike_id}
    bike["status"] = "reserved"

    log_cfg.audit_log("RESERVATION_CREATE", user_id, bike_id, ip=ip)
    bound_logger.info(f"Reservation {reservation_id} created successfully")
    return reservation_id

def start_rental(user_id, reservation_id, ip="127.0.0.1"):
    correlation_id = log_cfg.set_correlation_id()
    bound_logger = log_cfg.logger.bind(correlation_id=correlation_id)
    bound_logger.info("Starting rental")

    reservation = store.reservations.get(reservation_id)
    if not reservation or reservation["user_id"] != user_id:
        bound_logger.warning(f"Reservation {reservation_id} not found or invalid user")
        return None

    bike_id = reservation["bike_id"]
    bike = store.bikes.get(bike_id)
    if not bike or bike["status"] != "reserved":
        bound_logger.warning(f"Bike {bike_id} is not reserved")
        return None

    rental_id = str(uuid.uuid4())
    store.rentals[rental_id] = {"user_id": user_id, "bike_id": bike_id}
    bike["status"] = "rented"
    del store.reservations[reservation_id]

    log_cfg.audit_log("RENTAL_START", user_id, bike_id, ip=ip)
    bound_logger.info(f"Rental {rental_id} started successfully")
    return rental_id

def end_rental(user_id, rental_id, ip="127.0.0.1"):
    correlation_id = log_cfg.set_correlation_id()
    bound_logger = log_cfg.logger.bind(correlation_id=correlation_id)
    bound_logger.info("Ending rental")

    rental = store.rentals.get(rental_id)
    if not rental or rental["user_id"] != user_id:
        bound_logger.warning(f"Rental {rental_id} not found or invalid user")
        return None

    bike_id = rental["bike_id"]
    bike = store.bikes.get(bike_id)
    if not bike or bike["status"] != "rented":
        bound_logger.warning(f"Bike {bike_id} is not rented")
        return None

    bike["status"] = "available"
    del store.rentals[rental_id]

    log_cfg.audit_log("RENTAL_END", user_id, bike_id, ip=ip)
    bound_logger.info(f"Rental {rental_id} ended successfully")
    return True

def login_user(user_id, password, ip="127.0.0.1"):
    correlation_id = log_cfg.set_correlation_id()
    bound_logger = log_cfg.logger.bind(correlation_id=correlation_id)
    bound_logger.info("User login attempt")

    user = store.users.get(user_id)
    if not user or user["password"] != password:
        bound_logger.warning(f"Login failed for user {user_id}")
        log_cfg.audit_log("LOGIN_FAILURE", user_id, ip=ip)
        return False

    log_cfg.audit_log("LOGIN_SUCCESS", user_id, ip=ip)
    bound_logger.info(f"User {user_id} logged in successfully")
    return True

def update_inventory(admin_id, bike_id, delta, ip="127.0.0.1"):
    correlation_id = log_cfg.set_correlation_id()
    bound_logger = log_cfg.logger.bind(correlation_id=correlation_id)
    bound_logger.info("Updating inventory")

    admin = store.users.get(admin_id)
    if not admin or admin.get("role") != "admin":
        bound_logger.warning(f"Unauthorized admin {admin_id}")
        return False

    bike = store.bikes.get(bike_id)
    if not bike:
        bound_logger.warning(f"Bike {bike_id} not found")
        return False

    bike["inventory"] = bike.get("inventory", 0) + delta

    log_cfg.audit_log("ADMIN_INVENTORY_UPDATE", admin_id, bike_id, ip=ip)
    bound_logger.info(f"Bike {bike_id} inventory updated successfully")
    return True
    
    