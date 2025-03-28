from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, status, Form, UploadFile, File, Depends, Response
from typing import Annotated, Optional
from utils import db_dependency
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from models import User, NFT, Bid, Wallet, Setting, Deposit, Withdraw, Transaction
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from utils import hash_password, verify_password
import os
from starlette.datastructures import Headers
import io
#from sqlalchemy_file import File
from fastapi import FastAPI, BackgroundTasks

from email_temp import send_welcome_email






router = APIRouter(prefix='',tags=['Home'])

templates = Jinja2Templates(directory="templatesa")








@router.get("/cre", response_class=HTMLResponse)
async def reada_item(request: Request, db: db_dependency, error_message: str = ""):

    user_id = request.session.get("user_id")
    email = request.session.get("email")

    user = db.exec(select(User).where(User.id == user_id)).first()
    print("user", user)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    


    settings = db.exec(select(Setting).where(Setting.id == 1)).first()
    gas_fee = settings.gas
    


    
    

    


    return templates.TemplateResponse(request=request,  name="create-new.html", context={"user": user, "error_message": error_message, "gas": gas_fee})


@router.post("/addnft", response_class=HTMLResponse)
async def add_item(request: Request, db: db_dependency, image: UploadFile =File(...), name: str = Form(...), discription: str = Form(...), current_price: str = Form(...),no_of_copies: str = Form(...), error_message: str = ""):


    user_id = request.session.get("user_id")
    email = request.session.get("email")
    print("image", image)

    user = db.exec(select(User).where(User.id == user_id)).first()
    print("user", user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    

    settings = db.exec(select(Setting).where(Setting.id == 1)).first()
    gas_fee = settings.gas

    

    # Check if user has enough ETH balance
    if user.eth_balance < gas_fee:
        error_message = "Your ETH balance is not enough for the gas fee."
        return templates.TemplateResponse(
            request=request, name="create-new.html", context={"user": user, "error_message": error_message}
        )

    # Deduct gas fee
    user.eth_balance -= gas_fee

    # Fetch collections owned by the user
    nft_add = NFT(name=name, discription=discription, current_price=current_price, no_of_copies=no_of_copies, image=image, owner_id=user.id)
    db.add(nft_add)
    db.commit()
    db.refresh(nft_add)

    return RedirectResponse(url="/nft-collection", status_code=303)





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

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    
    statement = select(NFT)
    nftslive = db.exec(statement).all()

    if not user_id or not email:
        raise HTTPException(status_code=401, detail="User not authenticated")
    

    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()

    bid_stat = select(Bid).where(Bid.user_id==user.id)
    user_bids = db.exec(bid_stat).all()


    dp_stat = select(Deposit).where(Deposit.user_id==user.id)
    user_dp = db.exec(dp_stat).all()


    tran_stat = select(Transaction).where(Transaction.user_id==user.id)
    user_trans = db.exec(tran_stat).all()


    withdrawsta =select(Withdraw).where(Withdraw.user_id==user.id)
    usr_with = db.exec(withdrawsta).all()
        


    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={"nftlive": nftslive, "user": user, "bids": user_bids, "deposit": user_dp, "transaction": user_trans, "withdraw": usr_with})




@router.get("/view-nft/{address}", response_class=HTMLResponse)
async def view_nft_item(request: Request, address:str,  db: db_dependency):

    statement = select(NFT).where(NFT.eth_address==address)
    nft = db.exec(statement).first()

    astatement = select(NFT)
    nftslive = db.exec(astatement).all()

    bid_statement = select(Bid).join(NFT).where(NFT.eth_address==address)
    bids = db.exec(bid_statement).all()

    tran_statement = select(Transaction).join(NFT).where(NFT.eth_address==address)
    trans = db.exec(tran_statement).all()

    return templates.TemplateResponse(
        request=request, name="item-details.html", context={"nft": nft, "nftlive": nftslive, "bids": bids, "transactions": trans})


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, error_message: str = ""):
    return templates.TemplateResponse(
        request=request, name="login.html", context= {"request": request, "error_message": error_message})


@router.get("/wallet-connect", response_class=HTMLResponse)
async def logina(request: Request, db:db_dependency, error_message: str = ""):
    user_id = request.session.get("user_id")
    email = request.session.get("email")

    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse(
        request=request, name="my-wallet.html", context= {"request": request, "user": user, "error_message": error_message})


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
    return {"message": "Wallet is Importing, we will let you know when done", "wallet_id": wallet.id}



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
    background_tasks: BackgroundTasks,
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
    full_name = f"{first_name} {last_name}"
    background_tasks.add_task(send_welcome_email, email, full_name)

    
    request.session["user_id"] = new_user.id
    request.session["email"] = new_user.email



    return RedirectResponse(url="/dashboard", status_code=303)



@router.get("/nft-collection")
def register(
    request: Request,
    db: db_dependency,
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")
    base_url = str(request.base_url)  # Get the base URL dynamically


    user = db.exec(select(User).where(User.id == user_id)).first()

    nftstatement = select(NFT).where(NFT.owner_id==user.id)

    nfts = db.exec(nftstatement).all()

    return templates.TemplateResponse(
        request=request, name="my-collection.html",context= {"request": request, "user": user, "nfts": nfts })

@router.get("/live-bids")
def register(
    request: Request,
    db: db_dependency,
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")
    base_url = str(request.base_url)  # Get the base URL dynamically


    user = db.exec(select(User).where(User.id == user_id)).first()

    

    astatement = select(NFT)
    nftslive = db.exec(astatement).all()



    return templates.TemplateResponse(
        request=request, name="live-bids.html",context= {"request": request, "user": user, "nfts": nftslive })









@router.get("/profile/{wallet}")
def register(
    request: Request,
    db: db_dependency,
    wallet: str,
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")
    base_url = str(request.base_url)  # Get the base URL dynamically


    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.wallet_profile == wallet)).first()

    nftstatement = select(NFT).where(NFT.owner_id==user.id)

    nfts = db.exec(nftstatement).all()
    nfts_count = len(nfts)

    total_price = sum(nft.current_price for nft in nfts)

    transactions = db.exec(select(Transaction).where(Transaction.user_id==user.id)).all()


    return templates.TemplateResponse(
        request=request, name="author.html",context= {"request": request, "user": user, "nfts": nfts, "nfts_count": nfts_count, "total_price": total_price, "base_url": base_url, "transactions": transactions})



@router.get("/deposit/amount")
def register(
    request: Request,
    db: db_dependency,
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")


    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    return templates.TemplateResponse(
        request=request, name="deposit-amount-view.html",context= {"request": request, "user": user})



@router.get("/withdraw/amount")
def register(
    request: Request,
    db: db_dependency,
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")


    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    return templates.TemplateResponse(
        request=request, name="withdraw-amount.html",context= {"request": request, "user": user})




@router.post("/deposit/amount/confirm")
def register(
    request: Request,
    db: db_dependency,
    amount: str = Form(...),
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")

    settings = db.exec(select(Setting).where(Setting.id == 1)).first()
    wallet = settings.wallet_address
    request.session["amount"] = amount



    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    return templates.TemplateResponse(
        request=request, name="deposit-amount-confirm.html",context= {"request": request, "user": user, "wallet": wallet, "amount": amount})


@router.post("/withdraw-amount-confirm")
def register(
    request: Request,
    db: db_dependency,
    amount: str = Form(...),
    wallet: str = Form(...),
    error_message = ""
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")

    
    
    
    error_message = ""




    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()

    if user.eth_balance < 5.0:
        error_message = "Your Balance is not Up to 5 ETH"
        return templates.TemplateResponse(
        request=request, name="withdraw-amount.html",context= {"request": request, "user": user, "error": error_message})
    
    if float(amount) > user.eth_balance:
        error_message = f"Your Balance is not Up to {amount}"
        return templates.TemplateResponse(
        request=request, name="withdraw-amount.html",context= {"request": request, "user": user, "error": error_message})


    user.eth_balance -= float(amount)
    db.commit()

    new_withdraw = Withdraw(amount=amount, user_id=user.id, wallet=wallet)
    db.add(new_withdraw)
    db.commit()


    return templates.TemplateResponse(
        request=request, name="withdraw-confirm.html",context= {"request": request, "user": user, "amount": amount})




@router.get("/deposit/submit")
def register(
    request: Request,
    db: db_dependency,
    
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")
    amount = request.session.get("amount")

    settings = db.exec(select(Setting).where(Setting.id == 1)).first()
    wallet = settings.wallet_address



    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    return templates.TemplateResponse(
        request=request, name="deposit-submit.html",context= {"request": request, "user": user, "amount": amount})




@router.post("/deposit/complete")
def register(
    request: Request,
    db: db_dependency,
    proof: UploadFile =File(...),
    reference: str = Form(...),
    
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")
    amount = request.session.get("amount")


    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    new_deposit = Deposit(amount=amount, proof=proof, reference=reference, user_id=user_id)

    db.add(new_deposit)
    db.commit()
    db.refresh(new_deposit)


    return templates.TemplateResponse(
        request=request, name="deposit-complete.html",context= {"request": request, "user": user, "amount": amount})





@router.get("/withdraw/amount")
def register(
    request: Request,
    db: db_dependency,
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")


    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    return templates.TemplateResponse(
        request=request, name="withdraw-amount-view.html",context= {"request": request, "user": user})




@router.post("/withdraw/submit")
def register(
    request: Request,
    db: db_dependency,
    amount: float = Form(...),
    wallet_address: str = Form(...),
    error_message: str = ""

    
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")



    error_message = ""

    
    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()

    if amount < 3.0:
        error_message = "The Minimal Withdraw is 3 ETH"
        return templates.TemplateResponse(
        request=request, name="withdraw-amount-view.html",context= {"request": request, "user": user, "error_message": error_message})

    if user.eth_balance < amount or amount > user.eth_balance:
        error_message = f"Your Current Balance is {user.eth_balance}"
        return templates.TemplateResponse(
        request=request, name="withdraw-amount-view.html",context= {"request": request, "user": user, "error_message": error_message})
    
    

    user.eth_balance -= amount

    new_with = Withdraw(user_id=user.id, amount=amount, wallet=wallet_address)
    db.add(new_with)
    db.commit()
    db.refresh(new_with)



    return templates.TemplateResponse(
        request=request, name="withdraw-complete.html",context= {"request": request, "user": user, "amount": amount})





@router.get("/nft-trade")
def register(
    request: Request,
    db: db_dependency,
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")


    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    return templates.TemplateResponse(
        request=request, name="nft-trade.html",context= {"request": request, "user": user})



@router.get("/swap-nft")
def register(
    request: Request,
    db: db_dependency,
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")


    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    return templates.TemplateResponse(
        request=request, name="swap-nft.html",context= {"request": request, "user": user})




@router.get("/terms")
def register(
    request: Request,
    db: db_dependency,
):
    user_id = request.session.get("user_id")
    email = request.session.get("email")


    # Fetch user details from the database using session data
    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()


    return templates.TemplateResponse(
        request=request, name="terms.html",context= {"request": request, "user": user})







@router.get("/buy-nft/{address}", response_class=HTMLResponse)
async def view_nftj_item(request: Request, address:str,  db: db_dependency, error_message: str = "" ):

    statement = select(NFT).where(NFT.eth_address==address)
    nft = db.exec(statement).first()

    error_message = ""


    user_id = request.session.get("user_id")
    email = request.session.get("email")

    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()

    print("user:", user)


    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    

    if nft.no_of_copies == 0:
        error_message = "NFT is SOLD OUT"
        return templates.TemplateResponse(
        request=request, name="item-details.html",context= {"request": request, "user": user, "error_message": error_message, "nft": nft})

    


    if  user.eth_balance < nft.current_price:
        error_message = "Insuficient ETH Balance"
        return templates.TemplateResponse(
        request=request, name="item-details.html",context= {"request": request, "user": user, "error_message": error_message, "nft": nft})

    user.eth_balance -= nft.current_price
    nft.no_of_copies -=1
    db.commit()

    owner = nft.owner_id

    userpay = db.exec(select(User).where(User.id == owner)).first()
    userpay.eth_balance += nft.current_price
    db.commit()

    image_path = nft.image  # Assuming this is a valid file path


    new_nft = NFT(
        name=nft.name,
        discription=nft.discription,
        current_price=nft.current_price,
        owner_id=user.id,  # Assign to the new user
        image=image_path,    # Pass the file object
        no_of_copies=1
    )

    db.add(new_nft)
    db.commit()


    
    new_transbuy = Transaction(amount=nft.current_price, type="Buy", user_id=user.id, nft_id=nft.id)
    new_transsell = Transaction(amount=nft.current_price, type="Sell", user_id=userpay.id, nft_id=nft.id)
    db.add(new_transbuy)
    db.add(new_transsell)
    db.commit()


    
    return RedirectResponse(url="/nft-collection", status_code=303)






@router.get("/bid-nft/{address}", response_class=HTMLResponse)
async def view_nftj_item(request: Request, address:str,   db: db_dependency, error_message: str = "" , amount: float = Form):

    statement = select(NFT).where(NFT.eth_address==address)
    nft = db.exec(statement).first()

    error_message = ""


    user_id = request.session.get("user_id")
    email = request.session.get("email")

    user = db.exec(select(User).where(User.id == user_id, User.email == email)).first()

    print("user:", user)


    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    

    if  user.eth_balance < nft.current_price:
        error_message = "Insuficient ETH Balance"
        return templates.TemplateResponse(
        request=request, name="item-details.html",context= {"request": request, "user": user, "error_message": error_message, "nft": nft})

    
    

    new_bid = Bid(amount=amount,user_id=user.id,nft_id=nft.id)
    

    db.add(new_bid)
    db.commit()

    nft.current_price =amount
    db.commit()
    
    return RedirectResponse(url=f"/view-nft/{nft.eth_address}", status_code=303)



@router.get("/logout")
def logout(request: Request, response: Response):
    # Check if user is logged in
    user_id = request.session.get("user_id")
    if user_id:
        # Clear session data
        request.session.clear()
    
    # Redirect to login or homepage
    return RedirectResponse(url="/login", status_code=303)


