from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Account, Transaction
from app.schemas import TransactionCreate, TransactionRead
from app.dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# CREATE
@router.post("/", response_model=TransactionRead)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Verify account belongs to user
    account = db.query(Account).filter(
        Account.id == transaction.account_id,
        Account.user_id == int(current_user)
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or not owned by user")
    
    # Validate transaction data is positive
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Transaction amount must be positive")


    # new_transaction = Transaction(**transaction.dict())

    # Link transaction to user via account
    new_transaction = Transaction(
        user_id=int(current_user),
        account_id=transaction.account_id,
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category,
        date=transaction.date,
        plaid_transaction_id=getattr(transaction, "plaid_transaction_id", None)  # optional Plaid field
    )
    db.add(new_transaction)

    # Update account balance
    if transaction.type.lower() == "income":
        account.balance += transaction.amount
    elif transaction.type.lower() == "expense":
        account.balance -= transaction.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    db.commit()
    db.refresh(new_transaction)
    return new_transaction

# READ ALL
@router.get("/", response_model=list[TransactionRead])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    transactions = (
        db.query(Transaction)
        .join(Account)
        .filter(Account.user_id == int(current_user))
        .all()
    )
    return transactions

# READ ONE
@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    transaction = (
        db.query(Transaction)
        .join(Account)
        .filter(
            Transaction.id == transaction_id,
            Account.user_id == int(current_user)
        )
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction

# DELETE
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    transaction = (
        db.query(Transaction)
        .join(Account)
        .filter(
            Transaction.id == transaction_id,
            Account.user_id == int(current_user)
        )
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Adjust balance before delete
    if transaction.type.lower() == "income":
        transaction.account.balance -= transaction.amount
    elif transaction.type.lower() == "expense":
        transaction.account.balance += transaction.amount

    db.delete(transaction)
    db.commit()
    return

# UPDATE
@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Fetch existing transaction and validate user owns it
    transaction = (
        db.query(Transaction)
        .join(Account)
        .filter(
            Transaction.id == transaction_id,
            Account.user_id == int(current_user)
        )
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Fetch account for balance adjustments
    account = transaction.account

    # Reverse previous balance
    if transaction.type.lower() == "income":
        account.balance -= transaction.amount
    elif transaction.type.lower() == "expense":
        account.balance += transaction.amount

    # Validate new transaction amount
    if transaction_update.amount <= 0:
        raise HTTPException(status_code=400, detail="Transaction amount must be positive")

    # Apply updates
    transaction.amount = transaction_update.amount
    transaction.type = transaction_update.type
    transaction.category = transaction_update.category
    transaction.date = transaction_update.date
    transaction.plaid_transaction_id = getattr(transaction_update, "plaid_transaction_id", None)

    # Adjust balance with new values
    if transaction.type.lower() == "income":
        account.balance += transaction.amount
    elif transaction.type.lower() == "expense":
        account.balance -= transaction.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    db.commit()
    db.refresh(transaction)
    return transaction