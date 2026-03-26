import json
from datetime import date
from typing import List, Optional, Dict, Any, Tuple, Union
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic
from starlette.responses import Response
from dbcontroller import (DBController)
from datetime import datetime

# creating a FastAPI object
app = FastAPI()
security = HTTPBasic()

# configuring the static, which serve static
app.mount("/static", StaticFiles(directory="static"), name="static")

# adding the Session Middleware
app.add_middleware(SessionMiddleware, secret_key="MyApp")

# configuring the HTML pages
templates = Jinja2Templates(directory="templates")

# constant name for DATABASE_NAME
DATABASE_NAME = "app.db"
db = DBController(DATABASE_NAME)


# --- HELPER FUNCTIONS ---
def get_user_data(request: Request) -> Dict[str, Any]:
    """Retrieves user data dictionary if logged in."""
    user_data = {}
    if request.session.get("isLogin"):
        user_id = request.session.get("user_id")
        user_records = db.executeQueryWithParams(
            "SELECT * FROM users WHERE id = ?", [user_id]
        )
        if user_records:
            user_data = dict(user_records[0])
    return user_data


def get_rooms_details() -> List[Dict[str, Any]]:
    """Fetches and prepares room details."""
    rows = db.executeQuery(
        """
        SELECT name, desc, price, image, total_rooms, available_rooms
        FROM rdetails
    """
    )
    rooms = [dict(row) for row in rows]
    for room in rooms:
        room["is_full"] = room.get("available_rooms", 0) <= 0
    return rooms


def get_facility_details() -> List[Dict[str, Any]]:
    """Fetches and prepares facility details."""
    rows = db.executeQuery(
        """
        SELECT name, desc, price, image, total_slots, available_slots
        FROM factdetails
    """
    )
    facilities = [dict(row) for row in rows]
    for facility in facilities:
        facility["is_full"] = facility.get("available_slots", 0) <= 0
    return facilities


# --- AUTH HELPERS ---
def is_user_logged_in(request: Request) -> bool:
    return bool(request.session.get("isLogin")) and request.session.get("user_id") is not None


def is_admin_logged_in(request: Request) -> bool:
    return bool(request.session.get("isLogin")) and request.session.get("uid") is not None


def parse_facilities(other_facilities: Optional[str]) -> List[str]:
    """Parses the comma-separated `other_facilities` stored in `bdetails`."""
    if not other_facilities:
        return []
    return [x.strip() for x in other_facilities.split(",") if x.strip()]


# --- USER ROUTES ---
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/gallery", response_class=HTMLResponse)
def gallery(request: Request):
    return templates.TemplateResponse("gallery.html", {"request": request})


@app.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
    """Clear session and redirect to home."""
    request.session.clear()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.get("/reservations", response_class=HTMLResponse)
def reservation(request: Request):
    if not is_user_logged_in(request):
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    user_data = get_user_data(request)
    rooms_data = get_rooms_details()
    facilities_data = get_facility_details()

    return templates.TemplateResponse(
        "reservations.html",
        {
            "request": request,
            "user": user_data,
            "rdetails": rooms_data,
            "factdetails": facilities_data,
        },
    )


@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/footer", response_class=HTMLResponse)
def footer(request: Request):
    return templates.TemplateResponse("footer.html", {"request": request})


@app.get("/mainheader", response_class=HTMLResponse)
def mainheader(request: Request):
    return templates.TemplateResponse("mainheader.html", {"request": request})


@app.get("/rooms", response_class=HTMLResponse)
def rooms(request: Request):
    rooms_data = get_rooms_details()
    return templates.TemplateResponse("rooms.html", {"request": request, "rdetails": rooms_data})


@app.get("/facilities", response_class=HTMLResponse)
def facilities(request: Request):
    facilities_data = get_facility_details()
    return templates.TemplateResponse("facilities.html", {"request": request, "factdetails": facilities_data})


@app.post("/login", response_class=HTMLResponse)
def do_login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
):
    # Retrieve user by email
    user_records = db.executeQueryWithParams("SELECT * FROM users WHERE email = ?", [email])

    if not user_records:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid email or Password"})

    user = dict(user_records[0])
    stored_password = str(user.get("password", ""))

    if password != stored_password:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid email or Password"})
    
    # Store all relevant info in session
    request.session["isLogin"] = True
    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]
    request.session["email"] = user["email"]
    request.session["mobileno"] = user["mobileno"]

    return RedirectResponse("/reservations", status_code=status.HTTP_302_FOUND)


@app.post("/signup", response_class=HTMLResponse)
def do_signup(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), mobileno: str = Form(...)):

    existing_user = db.executeQueryWithParams("select * from users where email = ?", [email])

    if existing_user:
        return templates.TemplateResponse("signup.html", {"request": request, "msg": "User with this email already exists. Please login."})
    else:
        
        try:
            mobileno_int = int(mobileno)
        except ValueError:
            return templates.TemplateResponse("signup.html", {"request": request, "msg": "Mobile number must be numeric."})


        user = {
            "username": username,
            "password": password,
            "email": email,
            "mobileno": mobileno_int,
        }

        db.insert("users", user)
        print(f"SUCCESS: User {email} registered.")
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "msg": "You have successfully created an account. Please login.",
            },
        )

@app.post("/reservations", response_class=HTMLResponse)
def do_reservation(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    telphone: str = Form(...),
    address: str = Form(...),
    Room_type: Optional[str] = Form(None),
    facility_name: Optional[List[str]] = Form(
        None
    ),
    number_of_rooms: int = Form(1),
    arrival_date: str = Form(...),
    departure_date: str = Form(...),
):
    if not is_user_logged_in(request):
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    user_data = get_user_data(request)
    rooms_data = get_rooms_details()
    facilities_data = get_facility_details()
    context = {
        "request": request,
        "user": user_data,
        "rdetails": rooms_data,
        "factdetails": facilities_data,
    }

    def render_error(msg: str):
        context["msg"] = msg
        return templates.TemplateResponse("reservations.html", context)

    try:
        arrival_date_dt = datetime.strptime(arrival_date, "%Y-%m-%d")
        departure_date_dt = datetime.strptime(departure_date, "%Y-%m-%d")
    except ValueError:
        return render_error("Invalid date format.")

    if departure_date_dt <= arrival_date_dt:
        return render_error("Departure date must be after arrival date.")

    try:
        telphone_int = int(telphone)
    except ValueError:
        return render_error("Internal error processing telephone number.")

    final_room_type = Room_type.strip() if Room_type else None

    facilities_to_book: List[str] = facility_name if facility_name is not None else []

    db_facility_string: Optional[str] = (
        ", ".join(facilities_to_book) if facilities_to_book else None
    )

    if number_of_rooms <= 0 or not final_room_type:
        return render_error(
            "A reservation must include at least one room and a valid Room Type. Facilities are optional."
        )

    transaction_list: List[Tuple[str, Union[List[Any], Dict[str, Any]]]] = []

    if final_room_type:
        print(f"🔍 Checking room availability for: '{final_room_type}'")
        room_result = db.executeQueryWithParams(
            "SELECT available_rooms FROM rdetails WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))",
            [final_room_type],
        )

        if not room_result:
            return render_error(f"Room type '{final_room_type}' not found.")

        room = dict(room_result[0])
        available_rooms = room.get("available_rooms", 0)

        if available_rooms >= number_of_rooms:
            room_update_query = "UPDATE rdetails SET available_rooms = available_rooms - ? WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))"
            room_update_params = [number_of_rooms, final_room_type]
            transaction_list.append((room_update_query, room_update_params))
            print(f" Room update queued: {final_room_type} (-{number_of_rooms})")
        else:
            print(f" Not enough rooms: only {available_rooms} left.")
            return render_error(
                f"Only {available_rooms} {final_room_type}(s) available."
            )

    if facilities_to_book:
        print(f"🔍 Checking {len(facilities_to_book)} facilities for slots.")

        for fac_name in facilities_to_book:
            fac_result = db.executeQueryWithParams(
                "SELECT available_slots FROM factdetails WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))",
                [fac_name],
            )

            if not fac_result:
                return render_error(f"Facility '{fac_name}' not found. No booking action taken.")

            facility_data = dict(fac_result[0])
            available_slots = facility_data.get("available_slots", 0)

            if available_slots <= 0:
                print(f" Facility full: {fac_name}")
                return render_error(
                    f"{fac_name} is fully booked. No booking action taken."
                )

            fac_update_query = "UPDATE factdetails SET available_slots = available_slots - 1 WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))"
            fac_update_params = [fac_name]
            transaction_list.append((fac_update_query, fac_update_params))
            print(f" Facility update queued: {fac_name} (-1)")

    bdetail = {
        "name": name,
        "email": email,
        "telphone": telphone_int,
        "address": address,
        "room_type": final_room_type,
        "number_of_rooms": number_of_rooms,
        "other_facilities": db_facility_string,
        "arrival_date": arrival_date,
        "departure_date": departure_date,
    }

    columns = ", ".join(bdetail.keys())
    placeholders = ":" + ", :".join(bdetail.keys()) 
    booking_insert_query = f"INSERT INTO bdetails ({columns}) VALUES ({placeholders})"

    transaction_list.append((booking_insert_query, bdetail))

    try:
        db.executeTransaction(transaction_list)
        print(" SUCCESS: Transaction complete (Room, Facilities, Booking committed).")
        return render_error("Booking was successful!")
    except Exception as e:
        print(f"!!! CRITICAL TRANSACTION ERROR (Rollback completed): {e}")
        return render_error(
            f"Booking failed due to a severe database error. All availability changes were rolled back automatically. Error: {e}"
        )

@app.get("/my/reservations", response_class=HTMLResponse)
def my_reservations(request: Request):
    if not is_user_logged_in(request):
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    email = request.session.get("email")
    bookings = db.executeQueryWithParams("SELECT * FROM bdetails WHERE email = ?", [email])

    return templates.TemplateResponse(
        "my_reservations.html",
        {"request": request, "bdetails": bookings},
    )


@app.post("/reservations/{reservation_id}/cancel", response_class=HTMLResponse)
def cancel_reservation(request: Request, reservation_id: int):
    if not is_user_logged_in(request):
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    email = request.session.get("email")
    booking_rows = db.executeQueryWithParams(
        "SELECT * FROM bdetails WHERE id = ? AND email = ?",
        [reservation_id, email],
    )
    if not booking_rows:
        return RedirectResponse("/my/reservations", status_code=status.HTTP_302_FOUND)

    booking = dict(booking_rows[0])
    room_type = booking.get("room_type")
    number_of_rooms = int(booking.get("number_of_rooms") or 0)
    facilities = parse_facilities(booking.get("other_facilities"))

    transaction_list: List[Tuple[str, Union[List[Any], Dict[str, Any]]]] = []

    if room_type and number_of_rooms > 0:
        transaction_list.append(
            (
                "UPDATE rdetails SET available_rooms = available_rooms + ? "
                "WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))",
                [number_of_rooms, room_type],
            )
        )

    for fac_name in facilities:
        transaction_list.append(
            (
                "UPDATE factdetails SET available_slots = available_slots + 1 "
                "WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))",
                [fac_name],
            )
        )

    transaction_list.append(("DELETE FROM bdetails WHERE id = ?", [reservation_id]))

    db.executeTransaction(transaction_list)
    return RedirectResponse("/my/reservations", status_code=status.HTTP_302_FOUND)


# --- ADMIN ROUTES ---
@app.get("/admin/reservations", response_class=HTMLResponse)
def admin_reservations(request: Request):
    if not is_admin_logged_in(request):
        return RedirectResponse("/admin/login", status_code=status.HTTP_302_FOUND)

    # Fetch all bookings
    bookings = db.executeQuery("SELECT * FROM bdetails")

    # Fetch room availability summary
    rooms = db.executeQuery(
        """
        SELECT 
            name,
            total_rooms,
            available_rooms,
            (total_rooms - available_rooms) AS booked_rooms
        FROM rdetails
    """
    )

    # Fetch facility availability summary
    facilities = db.executeQuery(
        """
        SELECT 
            name,
            total_slots,
            available_slots,
            (total_slots - available_slots) AS booked_slots
        FROM factdetails
    """
    )

    return templates.TemplateResponse(
        "/admin/reservations.html",
        {
            "request": request,
            "bdetails": bookings,
            "rooms": rooms,
            "facilities": facilities,
        },
    )


@app.post("/admin/reservations/{reservation_id}/cancel", response_class=HTMLResponse)
def admin_cancel_reservation(request: Request, reservation_id: int):
    if not is_admin_logged_in(request):
        return RedirectResponse("/admin/login", status_code=status.HTTP_302_FOUND)

    booking_rows = db.executeQueryWithParams(
        "SELECT * FROM bdetails WHERE id = ?",
        [reservation_id],
    )
    if not booking_rows:
        return RedirectResponse("/admin/reservations", status_code=status.HTTP_302_FOUND)

    booking = dict(booking_rows[0])
    room_type = booking.get("room_type")
    number_of_rooms = int(booking.get("number_of_rooms") or 0)
    facilities = parse_facilities(booking.get("other_facilities"))

    transaction_list: List[Tuple[str, Union[List[Any], Dict[str, Any]]]] = []

    # Restore room availability
    if room_type and number_of_rooms > 0:
        transaction_list.append(
            (
                "UPDATE rdetails SET available_rooms = available_rooms + ? "
                "WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))",
                [number_of_rooms, room_type],
            )
        )

    # Restore facility availability (1 slot per facility per booking)
    for fac_name in facilities:
        transaction_list.append(
            (
                "UPDATE factdetails SET available_slots = available_slots + 1 "
                "WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))",
                [fac_name],
            )
        )

    transaction_list.append(("DELETE FROM bdetails WHERE id = ?", [reservation_id]))
    db.executeTransaction(transaction_list)
    return RedirectResponse("/admin/reservations", status_code=status.HTTP_302_FOUND)


@app.get("/admin/login", response_class=HTMLResponse)
def admin_logina(request: Request):
    return templates.TemplateResponse("/admin/login.html", {"request": request})


@app.get("/admin/adminheader", response_class=HTMLResponse)
def adminheader(request: Request):
    return templates.TemplateResponse("/admin/adminheader.html", {"request": request})


@app.post("/admin/login", response_class=HTMLResponse)
def do_admin_login(request: Request, email: str = Form(...), password: str = Form(...)):
    admin = db.executeQueryWithParams(
        "SELECT * FROM admins WHERE email=? AND password=?", [email, password]
    )

    if not admin:
        return templates.TemplateResponse(
            "/admin/login.html",
            {"request": request, "msg": "Invalid Email or Password"},
        )

    admin = admin[0]

    request.session.setdefault("isLogin", True)
    request.session.setdefault("username", admin["username"])
    request.session.setdefault("uid", admin["id"])

    return RedirectResponse("/admin/reservations", status_code=status.HTTP_302_FOUND)
