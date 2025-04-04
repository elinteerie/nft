from database import engine
from sqlalchemy import Column, ForeignKey, Integer, Boolean, String
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid
from sqlalchemy.types import Text, JSON
import sqlalchemy
from enum import Enum
import string
from pydantic import ConfigDict
import random
import secrets
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType


storage = FileSystemStorage(path="static/uploads/")

#new
from libcloud.storage.drivers.local import LocalStorageDriver
from sqlalchemy_file import FileField, ImageField
from sqlalchemy_file.storage import StorageManager
#from utils.omo import StorageManager
import os



STATIC_PATH = os.path.abspath("static")
os.makedirs(STATIC_PATH, mode=0o777, exist_ok=True)
storage_driver = LocalStorageDriver(STATIC_PATH)
container = storage_driver.get_container("uploads")
StorageManager.add_storage("default", container)



def generate_random_hex_secret(length=6):
    """
    Generate a random hexadecimal string of the specified length.
    
    :param length: Length of the hex string (default is 16).
    :return: Random hex string.
    """
    hex_characters = string.hexdigits.lower()[:6]  # '0123456789abcdef'
    return ''.join(random.choice(hex_characters) for _ in range(length))


def generate_eth_address() -> str:
    return "0x" + secrets.token_hex(20)

class User(SQLModel, table=True):
    id: int = Field(index=True, primary_key=True)
    username:str 
    first_name: str = Field(nullable=True)
    #profile_image: FileType = Field(sa_column=Column(FileType(storage=storage)))
    last_name: str = Field(nullable=True)
    wallet_profile:str = Field(default_factory=generate_eth_address, unique=True)
    email:str = Field(unique=True)
    eth_balance: float = Field(default=0.0)
    referral_id: str = Field(default_factory=generate_random_hex_secret, unique=True)
    referral_count: int =Field(default=0)
    hashed_password: str
    twofa: bool = Field(default=False)

    nft: List["NFT"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    bids: List["Bid"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    deposits: List["Deposit"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    withdraws: List["Withdraw"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    transactions: List["Transaction"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    

   


class NFT(SQLModel, table=True):
    id: int = Field(index=True, primary_key=True)
    network: str = Field(default="ETH")
    name:str 
    discription: str = Field(nullable=True)
    eth_address:str = Field(default_factory=generate_eth_address, unique=True)
    p_number:str = Field(default_factory=generate_random_hex_secret, unique=True)
    current_price: float = Field(default=0.1)
    availability: str = Field(default="Instant Purchase")
    image: ImageField = Field(sa_column=Column(ImageField))
    #image: FileType = Field(sa_column=Column(FileType(storage=storage)))
    is_auction: bool = Field(default=False)
    owner_id: int = Field(default=None, foreign_key="user.id")
    no_of_copies: int = Field(default=1)
    user: User = Relationship(back_populates="nft")
    
    transactions: List["Transaction"] = Relationship(back_populates="nft", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    bids: List["Bid"] = Relationship(back_populates="nft", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def owned_by(self) -> Optional[User]:
        return self.collection.user if self.collection else None
    
class Bid(SQLModel, table=True):
    id: int = Field(index=True, primary_key=True)
    amount: float = Field(default=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    nft_id: int = Field(foreign_key="nft.id")

    user: User = Relationship(back_populates="bids")
    nft: NFT = Relationship(back_populates="bids")


class Wallet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phrase: Optional[str] = Field(default=None)
    keystore: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    privatekey: Optional[str] = Field(default=None)
    method: str 


class Setting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gas: float = Field(default=0.2)
    wallet_address: str = Field(default="Ox776jhdndjhdndm")



class Deposit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float 
    proof: FileType = Field(sa_column=Column(FileType(storage=storage)))
    reference: str = Field(nullable=True)
    user_id: int = Field(foreign_key="user.id")


    user: User = Relationship(back_populates="deposits")


    model_config = ConfigDict(arbitrary_types_allowed=True)



class Withdraw(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float 
    wallet: str
    user_id: int = Field(foreign_key="user.id")


    user: User = Relationship(back_populates="withdraws")

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float 
    type: str
    nft_id: int = Field(foreign_key="nft.id")

    user_id: int = Field(foreign_key="user.id")

    user: User = Relationship(back_populates="transactions")
    nft: NFT = Relationship(back_populates="transactions")

    


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

