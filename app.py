from datetime import datetime
from unicodedata import name
from fastapi import FastAPI, Request, Cookie
from fastapi.params import Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dbcontroller import DBController
import datetime
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# creating a FastAPI object
app = FastAPI()
security = HTTPBasic()

# configuring the static, which serve static
app.mount("/static", StaticFiles(directory="static"), name="static")

# adding the Session Middleware
app.add_middleware(SessionMiddleware, secret_key='MyApp')

# configuring the HTML pages
templates = Jinja2Templates(directory="templates")

#constant name for DATABASE_NAME
DATABASE_NAME = "app.db"
db = DBController(DATABASE_NAME)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/gallery", response_class=HTMLResponse)
def gallery(request: Request):
    return templates.TemplateResponse("gallery.html", {"request": request})

@app.get("/reservations",response_class=HTMLResponse)
def reservation(request: Request):
    return templates.TemplateResponse("reservations.html", {"request": request})

@app.get("/login",response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup",response_class=HTMLResponse)
def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/admin/reservations",response_class=HTMLResponse)
def admin_reservations(request: Request):
    reservations = db.executeQuery("select * from bdetails")
    return templates.TemplateResponse("/admin/reservations.html", {"request": request, "bdetails": reservations})

@app.get("/admin/login",response_class=HTMLResponse)
def admin_logina(request: Request):
    return templates.TemplateResponse("/admin/login.html", {"request": request}) 


@app.post("/login", response_class=HTMLResponse)
def do_login(request: Request, response: Response, email: str = Form(...), password: str = Form(...)):
    user = db.executeQueryWithParams("select * from users where email =? and password=?", [email, password])
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid email or Password"})
    else:
        request.session.setdefault('isLogin', True)
        request.session.setdefault('username', user[0]['username'])
        request.session.setdefault('uid', user[0]['id'])
        return RedirectResponse("/reservations", status_code=status.HTTP_302_FOUND)
     
@app.post("/signup", response_class=HTMLResponse)
def do_signup(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...) ,mobileno: int = Form(...)):
    user = {"username":username,"password":password,"email":email ,"mobileno":mobileno}
    db.insert("users",user)    
    if user:
        return templates.TemplateResponse("signup.html", {"request": request, "msg": "you succesfully created a account please login"})
    else:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@app.post("/admin/login", response_class=HTMLResponse)
def do_login(request: Request, email: str = Form(...) , password: str = Form(...)):
    admin = db.executeQueryWithParams("select * from admins where email=? and password=?", [email, password])[0]
    if not admin:
        return templates.TemplateResponse("/admin/login", {"request": request, "msg": "Invalid Username or Password"})
    else:
        request.session.setdefault("isLogin", True)
        request.session.setdefault('username', admin['username'])
        request.session.setdefault('uid', admin['id'])
        return RedirectResponse("/admin/reservations", status_code=status.HTTP_302_FOUND)       

@app.get("/rooms", response_class=HTMLResponse)
def rooms(request: Request):
    rooms = db.executeQuery("select * from rdetails")
    for room in rooms:
        print(type(room))
    return templates.TemplateResponse("rooms.html", {"request": request, "rdetails": rooms})

@app.get("/facilities", response_class=HTMLResponse)
def facilities(request: Request):
    facilities = db.executeQuery("select * from factdetails")
    for facility in facilities:
        print(type(facility))
    return templates.TemplateResponse("facilities.html", {"request": request, "factdetails":facilities})

@app.post("/reservations",response_class=HTMLResponse)
def reservation(request: Request,name:str=Form(...), email:str=Form(...),telphone:int=Form(...),address:str=Form(...),Room_type:str=Form(...),number_of_rooms:str=Form(...),other_facilities:str=Form(...),arrival_data:str=Form(...),departure_date:str=Form(...)):
    bdetail = {"name":name,"email":email,"telphone":telphone,"address":address,"Room_type":Room_type,"number_of_rooms":number_of_rooms,"other_facilities":other_facilities,"arrival_date":arrival_data,"departure_date":departure_date}
    db.insert("bdetails",bdetail)
    return templates.TemplateResponse("/reservations.html", {"request": request, "msg": "Booking was successful"})
    
@app.get("/reservations", response_class=HTMLResponse)
def reservations(request: Request):
    reservations = db.executeQuery("select * from bdetails")
    for reservation in reservations:
        print(type(reservation))
    return templates.TemplateResponse("/admin/reservations.html", {"request": request, "bdetails": reservations})