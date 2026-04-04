from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User, Token
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.db.redis_client import redis_client
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str, db: AsyncSession = Depends(get_db)):
    # In a real app, you'd extract the token from the header automatically via dependency
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    jti = payload.get("jti")
    exp = payload.get("exp")
    
    if jti and exp:
        # Calculate remaining time until expiration
        from datetime import datetime
        now_ts = datetime.utcnow().timestamp()
        ttl = int(exp - now_ts)
        if ttl > 0:
            await redis_client.add_to_blacklist(jti, ttl)
            
    return {"message": "Successfully logged out"}

@router.get("/users/me", response_model=User)
async def read_users_me(token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    jti = payload.get("jti")
    if await redis_client.is_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Token has been revoked")
        
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user