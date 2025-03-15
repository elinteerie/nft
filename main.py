from fastapi import FastAPI
from database import engine, get_db
from contextlib import asynccontextmanager
from models import User, Collection, NFT, Bid, Wallet, Setting, Deposit, Withdraw
from models import create_db_and_tables
from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin import Admin, ModelView
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers import homepage
from utils import get_current_user, db_dependency

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request):
        form = await request.form()
        username, password = form["username"], form["password"]
        
        if username =='admin' and password == 'password':

        
            request.session.update({"token": "UUID"})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True

print("Phantom Desktop Wallet Connected.")
print("Mint 700,000 ETC Token")
print("Minting Started ..")
print("Minting in Progress please wait")
print("WalletSignTransaction")
print("Gas Fee -0.21")
print("Sucesss Please Click Explorer")
print("https://solscan.io/tx/2dHVBQCLjtuFuct66aHZJVfBcy4MsiSqYaeuf8dX91tmgy4Y1REnVcXPfyPq43czDHiYnSy69eb7oTEHD9Mn3jeb")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("db created ")
    create_db_and_tables()
    print("db updated")
    yield  # Your application runs during this yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



@app.middleware("http")
async def add_user_to_templates(request: Request, call_next):
    user = get_current_user(request)
    templates.env.globals["user"] = user  # Inject globally
    response = await call_next(request)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins          # Origins allowed to access your app
    allow_credentials=True,          # Allow cookies
    allow_methods=["*"],             # Allow all HTTP methods
    allow_headers=["*"],             # Allow all headers
)


authentication_backend = AdminAuth(secret_key="88")
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="88")

app.include_router(homepage.router)



class UserAdmin(ModelView, model=User):
    column_list = "__all__"

class CollectionAdmin(ModelView, model=Collection):
    column_list = "__all__"

class NFTAdmin(ModelView, model=NFT):
    column_list = "__all__"


class BidAdmin(ModelView, model=Bid):
    column_list = "__all__"

class WalletAdmin(ModelView, model=Wallet):
    column_list = "__all__"


class SettingAdmin(ModelView, model=Setting):
    column_list = "__all__"



class DepositAdmin(ModelView, model=Deposit):
    column_list = "__all__"


class WithdrawAdmin(ModelView, model=Withdraw):
    column_list = "__all__"




admin.add_view(UserAdmin)
admin.add_view(CollectionAdmin)
admin.add_view(NFTAdmin)
admin.add_view(BidAdmin)
admin.add_view(WalletAdmin)
admin.add_view(DepositAdmin)
admin.add_view(SettingAdmin)
admin.add_view(WithdrawAdmin)