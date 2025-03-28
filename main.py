from fastapi import FastAPI
from database import engine, get_db
from contextlib import asynccontextmanager
from models import User, NFT, Bid, Wallet, Setting, Deposit, Withdraw,Transaction
from models import create_db_and_tables
from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers import homepage
from starlette.responses import Response
from utils import get_current_user, db_dependency
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

users = {
    "admin": {
        "name": "Admin",
        "avatar": "admin.png",
        "company_logo_url": "admin.png",
        "roles": ["read", "create", "edit", "delete", "action_make_published"],
    },
    "johndoe": {
        "name": "John Doe",
        "avatar": None, # user avatar is optional
        "roles": ["read", "create", "edit", "action_make_published"],
    },
    "viewer": {"name": "Viewer", "avatar": "guest.png", "roles": ["read"]},
}


class UsernameAndPasswordProvider(AuthProvider):
    """
    This is only for demo purpose, it's not a better
    way to save and validate user credentials
    """

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if len(username) < 3:
            """Form data validation"""
            raise FormValidationError(
                {"username": "Ensure username has at least 03 characters"}
            )

        if username in users and password == "passwordy":
            """Save `username` in session"""
            request.session.update({"username": username})
            return response

        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        if request.session.get("username", None) in users:
            """
            Save current `user` object in the request state. Can be used later
            to restrict access to connected user.
            """
            request.state.user = users.get(request.session["username"])
            return True

        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        user = request.state.user  # Retrieve current user
        # Update app title according to current_user
        custom_app_title = "Hello, " + user["name"] + "!"
        # Update logo url according to current_user
        custom_logo_url = None
        if user.get("company_logo_url", None):
            custom_logo_url = request.url_for("static", path=user["company_logo_url"])
        return AdminConfig(
            app_title=custom_app_title,
            logo_url=custom_logo_url,
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user  # Retrieve current user
        photo_url = None
        if user["avatar"] is not None:
            photo_url = request.url_for("static", path=user["avatar"])
        return AdminUser(username=user["name"], photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("db created ")
    create_db_and_tables()
    print("db updated")
    yield  # Your application runs during this yield




app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templatesa")


from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi import  Path
from sqlalchemy_file.storage import StorageManager
from libcloud.storage.base import ObjectDoesNotExistError
from libcloud.storage.drivers.local import LocalStorageDriver

@app.get("/media/{storage}/{file_id}", response_class=FileResponse)
def serve_files(storage: str = Path(...), file_id: str = Path(...)):
    try:
        file = StorageManager.get_file(f"{storage}/{file_id}")
        if isinstance(file.object.driver, LocalStorageDriver):
            """If file is stored in local storage, just return a
            FileResponse with the fill full path."""
            return FileResponse(
                file.get_cdn_url(), media_type=file.content_type, filename=file.filename
            )
        elif file.get_cdn_url() is not None:
            """If file has public url, redirect to this url"""
            return RedirectResponse(file.get_cdn_url())
        else:
            """Otherwise, return a streaming response"""
            return StreamingResponse(
                file.object.as_stream(),
                media_type=file.content_type,
                headers={"Content-Disposition": f"attachment;filename={file.filename}"},
            )
    except ObjectDoesNotExistError:
        return JSONResponse({"detail": "Not found"}, status_code=404)






"""@app.middleware("http")
async def add_user_to_templates(request: Request, call_next):
    user = get_current_user(request)
    templates.env.globals["user"] = user  # Inject globally
    response = await call_next(request)
    return response"""


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins          # Origins allowed to access your app
    allow_credentials=True,          # Allow cookies
    allow_methods=["*"],             # Allow all HTTP methods
    allow_headers=["*"],             # Allow all headers
)



from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
app.add_middleware(SessionMiddleware, secret_key="88")

app.include_router(homepage.router)

admin = Admin(engine, auth_provider=UsernameAndPasswordProvider(), middlewares=[Middleware(SessionMiddleware, secret_key="88")])


admin.add_view(ModelView(User))
admin.add_view(ModelView(NFT))
admin.add_view(ModelView(Wallet))
admin.add_view(ModelView(Bid))
admin.add_view(ModelView(Transaction))
admin.add_view(ModelView(Withdraw))
admin.add_view(ModelView(Deposit))
admin.add_view(ModelView(Setting))
# Mount admin to your app
admin.mount_to(app)



