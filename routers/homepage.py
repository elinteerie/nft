from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, status, Form
from typing import Annotated, Optional
from utils import db_dependency
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from models import User, NFT, Bid, Wallet, Collection
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from utils import hash_password, verify_password




router = APIRouter(prefix='',tags=['Home'])

templates = Jinja2Templates(directory="templates")


@router.get("/cre", response_class=HTMLResponse)
async def read_item(request: Request):

    return templates.TemplateResponse(request=request,  name="create.html")



@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request, db: db_dependency):

    statement = select(NFT)
    nftslive = db.exec(statement).all()

    return templates.TemplateResponse(
        request=request, name="index.html", context={"nftlive": nftslive})



@router.get("/dashboard", response_class=HTMLResponse)
async def read_item(request: Request, db: db_dependency):

    user_id = request.session.get("user_id")
    email = request.session.get("email")

    
    statement = select(NFT)
    nftslive = db.exec(statement).all()

    if not user_id or not email:
        raise HTTPException(status_code=401, detail="User not authenticated")
    

    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={"nftlive": nftslive, "user": user})




@router.get("/view-nft/{address}", response_class=HTMLResponse)
async def view_nft_item(request: Request, address:str,  db: db_dependency):

    statement = select(NFT).where(NFT.eth_address==address)
    nft = db.exec(statement).first()

    astatement = select(NFT)
    nftslive = db.exec(astatement).all()

    bid_statement = select(Bid).join(NFT).where(NFT.eth_address==address)
    bids = db.exec(bid_statement).all()

    return templates.TemplateResponse(
        request=request, name="view-item.html", context={"nft": nft, "nftlive": nftslive, "bids": bids})


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, error_message: str = ""):
    return templates.TemplateResponse(
        request=request, name="login.html", context= {"request": request, "error_message": error_message})


@router.get("/wallet-connect", response_class=HTMLResponse)
async def logina(request: Request, error_message: str = ""):
    return templates.TemplateResponse(
        request=request, name="wallet-connect.html", context= {"request": request, "error_message": error_message})


@router.post("/addwallet")
def add_wallet(
    db: db_dependency,
    phrase: str = Form(None),
    keystore: str = Form(None),
    password: str = Form(None),
    privatekey: str = Form(None),
    method: str = Form("kaikas"),

):
    wallet = Wallet(
        phrase=phrase,
        keystore=keystore,
        password=password,
        privatekey=privatekey,
        method=method,
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return {"message": "Wallet added successfully", "wallet_id": wallet.id}



@router.post("/loginuser")
def login(
    request: Request,
    db: db_dependency,
    email: str = Form(...),
    password: str = Form(...),
    
):
    user = db.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        error_message ="Invalid email or password"
        return templates.TemplateResponse(request=request, name="login.html",context= {"request": request, "error_message": error_message})
    
    request.session["user_id"] = user.id
    request.session["email"] = user.email
    return RedirectResponse(url="/dashboard", status_code=303)



@router.get("/register", response_class=HTMLResponse)
def regi(request: Request, error_message: str = ""):
    return templates.TemplateResponse(
        request=request, name="register.html",context= {"request": request, "error_message": error_message})


@router.post("/registeruser")
def register(
    request: Request,
    db: db_dependency,
    first_name: str = Form(...),
    username: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),

):
    error_message = ""
    if password != confirm_password:
        error_message = "Passwords do not match"
        print(error_message)
        return templates.TemplateResponse(
            "register.html", context={"request": request, "error_message": error_message}
        )
    

    existing_user = db.exec(select(User).where(User.email == email)).first()
    if existing_user:
        error_message = "Email already registered"
        return templates.TemplateResponse(
            "register.html", context={"request": request, "error_message": error_message}
        )
    

    hashed_password = hash_password(password)
    new_user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    request.session["user_id"] = new_user.id
    request.session["email"] = new_user.email



    return RedirectResponse(url="/dashboard", status_code=303)



@router.get("/collection-create", response_class=HTMLResponse)
def regi(request: Request, error_message: str = ""):
    user_id = request.session.get("user_id")
    email = request.session.get("email")

    return templates.TemplateResponse(
        request=request, name="create-collection.html",context= {"request": request, "error_message": error_message})



@router.post("/createcollectionpost")
def register(
    request: Request,
    db: db_dependency,
    name: str = Form(...),
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")


    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    new_collection = Collection(
        name=name,
        owner_id=user.id
    )
    
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)

    return RedirectResponse(url="/dashboard", status_code=303)
    
