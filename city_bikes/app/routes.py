from fastapi import FastAPI
from pydantic import BaseModel
import app.services as services

app = FastAPI()

class ReservationRequest(BaseModel):
    bike_id: str
    user_id: str

class RentalStartRequest(BaseModel):
    user_id: str
    reservation_id: str

class RentalEndRequest(BaseModel):
    user_id: str
    rental_id: str

class LoginRequest(BaseModel):
    user_id: str
    password: str

class AdminInventoryRequest(BaseModel):
    admin_id: str
    bike_id: str
    delta: int

@app.get("/bikes")
def get_bikes_endpoint():
    return services.list_bikes() 

@app.post("/reservations")
def create_reservation(request: ReservationRequest):
    reservation_id = services.reserve_bike(request.bike_id, request.user_id)
    return {"reservation_id": reservation_id}

@app.post("/rentals/start")
def begin_rental(request: RentalStartRequest):
    rental_id = services.start_rental(request.user_id, request.reservation_id)
    return {"rental_id": rental_id}

@app.post("/rentals/end")
def finish_rental(request: RentalEndRequest):
    result = services.end_rental(request.user_id, request.rental_id)
    return result 

@app.post("/auth/login")
def login_user(request: LoginRequest):
    success = services.login_user(request.user_id, request.password)
    return {"success": success}

@app.post("/admin/inventory")
def admin_inventory(request: AdminInventoryRequest):
    services.update_inventory(request.admin_id, request.bike_id, request.delta)
    return {"status": "Inventory updated"}