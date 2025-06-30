from fastapi import FastAPI, File, UploadFile, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
from starlette.status import HTTP_302_FOUND
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import http_exception_handler
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.staticfiles import StaticFiles
from utils import json_to_dict_list
from typing import Optional
import json

from PIL import Image, ImageOps
import numpy as np
import io


from fastapi.security import APIKeyCookie
# from fastapi import FastAPI, File, UploadFile, 
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles

path_to_json = "users.json"



app = FastAPI()

# @app.get("/users")
# def get_all_users():
#     return json_to_dict_list(path_to_json)


@app.get("/users")
def get_all_users(
    enrollment_year: Optional[int] = None,
    major: Optional[str] = None,
    special_notes : Optional[str] = None,
    user_id : Optional[int] = None
    ):
    users = json_to_dict_list(path_to_json)
    # if enrollment_year is None:
    #     return users
    # else:
    #     return_list = []
    #     for user in users:
    #         if user["enrollment_year"] == enrollment_year:
    #             return_list.append(user)
    #     return return_list

    filltred_users = users
    if enrollment_year:
        filltred_users = [user for user in filltred_users if user["enrollment_year"] == enrollment_year]
    if major:
        filltred_users = [user for user in filltred_users if user["major"].lower() == major.lower()]
    if special_notes:
        filltred_users = [user for user in filltred_users if user["special_notes"].lower() == special_notes.lower()]
    if user_id:
        filltred_users = [user for user in filltred_users if user["user_id"] == user_id]
    
    return filltred_users

# @app.get("/users/{enrollment_year}")
# def get_all_users_enrollment_year(enrollment_year: int):
#     users = json_to_dict_list(path_to_json)
#     return_list = []
#     for user in users:
#         if user["enrollment_year"] == enrollment_year:
#             return_list.append(user)
#     return return_list


# @app.get("/users/{enrollment_year}")
# def get_all_users_enrollment_year(enrollment_year: int, major: Optional[str] = None, special_notes: Optional[str] = "Без особых примет"):
#     users = json_to_dict_list(path_to_json)
#     filltred_users = []
#     for user in users:
#         if user["enrollment_year"] == enrollment_year:
#             filltred_users.append(user)
#     if major:
#         filltred_users = [user for user in filltred_users if user["major"].lower() == major.lower()]
#     if special_notes:
#         filltred_users = [user for user in filltred_users if user["special_notes"].lower() == special_notes.lower()]
    
#     return filltred_users


# @app.get("/users/{user_id}")
# def get_all_users_enrollment_year(user_id: int, major: Optional[str] = None, special_notes: Optional[str] = "Без особых примет"):
#     users = json_to_dict_list(path_to_json)
#     filltred_users = []
#     for user in users:
#         if user["user_id"] == user_id:
#             filltred_users.append(user)
#     if major:
#         filltred_users = [user for user in filltred_users if user["major"].lower() == major.lower()]
#     if special_notes:
#         filltred_users = [user for user in filltred_users if user["special_notes"].lower() == special_notes.lower()]
    
#     return filltred_users


# @app.get("/users")
# def get_all_user(user_id: Optional[int] = None):
#     users = json_to_dict_list(path_to_json)
#     if user_id is None:
#         return users
#     else:
#         return_list = []
#         for user in users:
#             if user["user_id"] == user_id:
#                 return_list.append(user)
#         return return_list


# @app.get("/users")
# def get_all_users(enrollment_year: Optional[int] = None):
#     users = json_to_dict_list(path_to_json)
#     if enrollment_year is None:
#         return users
#     else:
#         return_list = []
#         for user in users:
#             if user["enrollment_year"] == enrollment_year:
#                 return_list.append(user)
#         return return_list

# @app.get("/users/")
# def get_user(user_id: Optional[int] = None):
#     users = json_to_dict_list(path_to_json)
#     if user_id is None:
#         return users
#     else:
#         return_list = []
#         for user in users:
#             if user["user_id"] == user_id:
#                 return_list.append(user)
#         return return_list
    


app.mount("/static", StaticFiles(directory="static"), name="static")

# шаблоны
templates = Jinja2Templates(directory="templates")
#
#

cookie_scheme = APIKeyCookie(name="session")

json_path = "/home/smile/converted_keras/users.json"

# users = {
#     "admin": "1234",
#     "user": "abcd",
#     "guest": "guest"
# }


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == HTTP_403_FORBIDDEN:
        return RedirectResponse("/login")
    # всё остальное отдаём штатному обработчику
    return await http_exception_handler(request, exc)


@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: str = Depends(cookie_scheme)):
    return templates.TemplateResponse("index.html", {"request": request, "user": session})

@app.get("/no_reg", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("no_reg.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# @app.post("/login")
# def login(username: str = Form(...), password: str = Form(...)):
#     if users.get(username) == password:
#         response = RedirectResponse("/", status_code=HTTP_302_FOUND)
#         response.set_cookie(key="session", value=username, httponly=True)
#         return response
#     raise HTTPException(status_code=401, detail="Неверный логин или пароль")



# Загрузка пользователей из JSON при старте приложения
with open("users.json", "r", encoding="utf-8") as f:
    users = json.load(f)

# Преобразуем в словарь для быстрого поиска: login -> password
user_credentials = {user["login"]: user["password"] for user in users}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username in user_credentials and user_credentials[username] == password:
        response = RedirectResponse("/", status_code=HTTP_302_FOUND)
        response.set_cookie(key="session", value=username, httponly=True)
        return response
    return RedirectResponse("/no_reg", status_code=302)


# @app.post("/login")
# def login(username: str = Form(...), password: str = Form(...)):
#     if users_login.get(login) == password:
#         response = RedirectResponse("/", status_code=HTTP_302_FOUND)
#         response.set_cookie(key="session", value=username, httponly=True)
#         return response
#     raise HTTPException(status_code=401, detail="Неверный логин или пароль")

@app.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=HTTP_302_FOUND)
    response.delete_cookie("session")
    return response



# @app.get("/login/")
# async def login(request: Request):
#     # Здесь можно добавить логику аутентификации
#     # Например, проверка логина и пароля
#     # Для простоты, просто создадим сессию
#     session_id = secrets.token_urlsafe(16)
#     response = RedirectResponse(url="/items/")
#     response.set_cookie(key="session", value=session_id)
#     return response 

# @app.get("/items/")
# async def read_items(session: str = Depends(cookie_scheme)):
#     return {"session": session}


# @app.get("/")
# def main_page(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# @app.get("/")
# def read_root():
#     return {"message": "API работает"}

# Загружаем модель один раз при старте сервера
model = load_model("keras_model.h5", compile=False)

# Загружаем метки классов
class_names = [line.strip() for line in open("labels.txt", "r").readlines()]

# session: str = Depends(cookie_scheme)
@app.post("/predict/")
async def predict(file: UploadFile = File(...), session: str = Depends(cookie_scheme)):
    # Читаем загруженный файл в память
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Обработка изображения
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # Предсказание
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = float(prediction[0][index])

    return JSONResponse(content={
        "class": class_name,
        "confidence": confidence_score
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)