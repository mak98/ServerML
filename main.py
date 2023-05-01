from fastapi import FastAPI, Request, Form,File, UploadFile,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic
from starlette.middleware.sessions import SessionMiddleware
from PIL import Image
import os
import io
from models import Models
from passlib.context import CryptContext
import mysql.connector
import json
# Create FastAPI instance
app = FastAPI()
# Add session middleware with secret key
app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")
# Mount static files directory to "/static"
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
security = HTTPBasic()
# Initialize password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="serverml"
)
mycursor = mydb.cursor()


# Initialize model handler for managing machine learning models
modelHandeler=Models("./static/uploads/")

# Login page route
@app.get("/")
def login(request: Request):
        if "flash" in request.session.keys():
            body={"request": request,"error":request.session["flash"]}
            request.session.pop("flash",None)
            return templates.TemplateResponse("login.html",body )
        return templates.TemplateResponse("login.html", {"request": request})
# Authentication route
@app.post("/login")
def authenticate_user(request: Request, email: str = Form(...), password: str = Form(...)):
    sql = "SELECT password FROM users WHERE email = %s"
    val = (email,)
    mycursor.execute(sql, val)
    user = mycursor.fetchone()
    if not user:
        request.session["flash"]="User Credentials Invalid"
        return RedirectResponse(url="/",status_code=303,headers={"x-error":"Invalid User Credentials"})
    if not pwd_context.verify(password, user[0]):
        request.session["flash"]="User Credentials Invalid"
        return RedirectResponse(url="/",status_code=303,headers={"x-error":"Invalid User Credentials"})
    request.session["user"]=email
    return RedirectResponse(url="/dashboard",status_code=303)

# Signup page route
@app.get("/signup")
def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


#user registration route
@app.post("/signup")
def add_user(request: Request, fname: str = Form(...),lname: str = Form(...),email: str = Form(...), password: str = Form(...),cpassword:str=Form(...)):
    mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    result = mycursor.fetchone()
    if result:
          return templates.TemplateResponse("signup.html", {"request":request,"error": "User Already Exists"})
    if password!=cpassword:
      return templates.TemplateResponse("signup.html", {"request":request,"error": "Passwords dont match"})
    hashed_password = pwd_context.hash(password)
    sql = "INSERT INTO users VALUES (%s, %s, %s, %s)"
    val = (email, hashed_password,fname,lname)
    mycursor.execute(sql, val)
    mydb.commit()
    request.session["user"]=email
    return RedirectResponse(url="/dashboard",status_code=303)

# Logout route
@app.get("/logout")
def logout(request:Request):
    if "user" in request.session.keys():
        # remove the "user" key from the session
        request.session.pop("user",None)
        return RedirectResponse(url="/")

# Dashboard route
@app.get("/dashboard")
def dashoard(request:Request):
    if "user" not in request.session.keys():
        return RedirectResponse(url="/",status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request})

#Upload access point for models and front end
@app.get("/upload")
async def card1(request: Request):
    if "user" not in request.session.keys():
        return RedirectResponse(url="/")
    return templates.TemplateResponse("upload.html", {"request": request})
@app.post("/upload")
async def upload_file(pt_file: UploadFile = File(...)):
    # get the file extension
    file_extension = os.path.splitext(pt_file.filename)[1]
    if file_extension != ".pt":
        return {"error": "Invalid file type. Only .pt files are allowed."}
    file_path = os.path.join("static", "uploads", pt_file.filename)
    with open(file_path, "wb") as f:
        contents = await pt_file.read()
        f.write(contents)
    # load the saved model in memory
    modelHandeler.loadModel(pt_file.filename,file_path)
    return RedirectResponse("/manage",status_code=303)


#Manage ML accesspoints
@app.get("/manage")
async def card2(request: Request):
    if "user" not in request.session.keys():
        return RedirectResponse(url="/")
    models=modelHandeler.getModel()
    return templates.TemplateResponse("manage.html", {"request": request,"models":models})
@app.get("/delete/{mname}")
async def delete_item(request: Request, mname: str):
    # drop the selected model
    modelHandeler.DropModel(mname)
    return RedirectResponse(url="/manage")

#Call Prediction 
@app.post("/predict/{mname}")
async def predict(request: Request,mname:str,file: UploadFile = File(...)):
    if mname not in modelHandeler.getModel():
        raise HTTPException(status_code=404, detail="Model not found")
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    prediction = modelHandeler.predict(mname,image)
    ret= {"prediction Index": prediction[0],"Raw Data":prediction[1]}
    return json.dumps(ret)