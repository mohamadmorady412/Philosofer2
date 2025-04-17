from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!super_secret_key!")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    # اگر session موجود باشه (یعنی کاربر وارد شده)
    username = request.session.get("username")
    if username:
        return templates.TemplateResponse(
            "home.html", {"request": request, "username": username}
        )
    return RedirectResponse("/login", status_code=302)


@app.get("/login")
async def get_login(request: Request):
    # اگر کاربر وارد شده بود، نباید دوباره به فرم لاگین بره
    username = request.session.get("username")
    if username:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/login")
async def post_login(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    # در صورتی که اطلاعات اشتباه وارد شد، session رو پاک می‌کنیم
    if request.session.get("username"):
        request.session.clear()

    # اگر اطلاعات درست وارد بشه، session رو ذخیره می‌کنیم
    if username == "admin" and password == "1234":
        request.session["username"] = username
        return templates.TemplateResponse(
            "home.html", {"request": request, "username": username}
        )

    # در غیر این صورت خطا رو نمایش می‌دهیم
    return templates.TemplateResponse(
        "form.html",
        {"request": request, "error": "❌ Username or password is incorrect."},
    )


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
