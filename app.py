from fastapi import FastAPI, File, UploadFile, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
from starlette.status import HTTP_302_FOUND
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.staticfiles import StaticFiles

from PIL import Image, ImageOps
import numpy as np
import io


from fastapi.security import APIKeyCookie
# from fastapi import FastAPI, File, UploadFile, 
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles





app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# шаблоны
templates = Jinja2Templates(directory="templates")
#
#

cookie_scheme = APIKeyCookie(name="session")

users = {
    "admin": "1234",
    "user": "abcd",
    "guest": "guest"
}


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == HTTP_403_FORBIDDEN:
        return RedirectResponse("/login")
    # всё остальное отдаём штатному обработчику
    return await http_exception_handler(request, exc)


@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: str = Depends(cookie_scheme)):
    return templates.TemplateResponse("index.html", {"request": request, "user": session})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if users.get(username) == password:
        response = RedirectResponse("/", status_code=HTTP_302_FOUND)
        response.set_cookie(key="session", value=username, httponly=True)
        return response
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")

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