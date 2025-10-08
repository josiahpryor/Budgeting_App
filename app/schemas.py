from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ===== AUTH SCHEMAS =====
class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ===== ACCOUNT & TRANSACTION SCHEMAS =====

class TransactionCreate(BaseModel):
    amount: float
    type: str  
    date: Optional[datetime] = None
    description: Optional[str] = None
    category: Optional[str] = None
    account_id: int
    plaid_transaction_id: str | None = None

class TransactionRead(TransactionCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
    plaid_transaction_id: str | None = None

class AccountCreate(BaseModel):
    name: str
    account_type: str
    balance: Optional[float] = 0.0
    plaid_account_id: str | None = None

class AccountRead(AccountCreate):
    id: int
    created_at: datetime
    transactions: List[TransactionRead] = []
    plaid_account_id: str | None = None

    class Config:
        orm_mode = True