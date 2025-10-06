from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Account, Transaction
from app.schemas import AccountCreate, AccountRead
from app.dependencies import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("/", response_model=AccountRead)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    new_account = Account(**account.dict(), user_id=int(current_user))
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

@router.get("/", response_model=list[AccountRead])
def get_accounts(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    accounts = db.query(Account).filter(Account.user_id == int(current_user)).all()
    return accounts