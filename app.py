import warnings

# Подавляем предупреждения об устаревших модулях в tensorflow и jax
warnings.filterwarnings("ignore", category=DeprecationWarning, module="tensorflow")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="jax")

import os
from argon2 import PasswordHasher
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
import uvicorn
from utils import json_to_dict_list
from typing import Optional
import json
# import tk
# from argon2 import PasswordHasher

from PIL import Image, ImageOps
import numpy as np
import io


from fastapi.security import APIKeyCookie
# from fastapi import FastAPI, File, UploadFile, 
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles


ph = PasswordHasher()

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


app.mount("/static", StaticFiles(directory="static"), name="static")

# шаблоны
templates = Jinja2Templates(directory="templates")
#
#

cookie_scheme = APIKeyCookie(name="session")

json_path = "/home/smile/converted_keras/users.json"



@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == HTTP_403_FORBIDDEN:
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)
    # всё остальное отдаём штатному обработчику
    return await http_exception_handler(request, exc)


@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: str = Depends(cookie_scheme)):
    return templates.TemplateResponse("index.html", {"request": request, "user": session})

@app.get("/no_reg", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("no_reg.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_p(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    # Загружаем текущий users.json
    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as f:
            users_list = json.load(f)
    else:
        users_list = []

    # Проверяем наличие пользователя
    hashed_password = ph.hash(password)
    if any(user["login"] == username and user[username] == hashed_password for user in users_list):
        # Если уже есть, перенаправляем
        return RedirectResponse("/", status_code=HTTP_302_FOUND)
    
    # Добавляем нового пользователя
    users_list.append({"login": username, "password": hashed_password})

    # Сохраняем обратно в файл
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users_list, f, ensure_ascii=False, indent=2)

    # Устанавливаем cookie и перенаправляем
    response = RedirectResponse("/login", status_code=HTTP_302_FOUND)
    return response


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    # Загрузка пользователей из JSON при старте приложения
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    user_credentials = {user["login"]: user["password"] for user in users}

    if username in user_credentials:

        try:
            if ph.verify(user_credentials[username], password):
                response = RedirectResponse("/", status_code=HTTP_302_FOUND)
                response.set_cookie(key="session", value=username, httponly=True)
                return response
        except Exception:
        # Ловим ошибку при неверном пароле
            return RedirectResponse("/no_reg", status_code=302)

    # Преобразуем в словарь для быстрого поиска: login -> password
    

    if username in user_credentials and user_credentials[username] == password:
        response = RedirectResponse("/", status_code=HTTP_302_FOUND)
        response.set_cookie(key="session", value=username, httponly=True)
        return response
    return RedirectResponse("/no_reg", status_code=302)


@app.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=HTTP_302_FOUND)
    response.delete_cookie("session")
    return response

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