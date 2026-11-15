from typing import List, Union
from fastapi import Request, HTTPException, status
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return {
        "user_id": user_id, "username": request.session.get("username"),
        "role": request.session.get("role"), "staff_id": request.session.get("staff_id"),
        "resident_id": request.session.get("resident_id")
    }

def require_role(roles: Union[str, List[str]]):
    allowed = [roles] if isinstance(roles, str) else list(roles)
    def role_checker(request: Request):
        user = get_current_user(request)
        if not user:
            raise HTTPException(status.HTTP_303_SEE_OTHER, headers={"Location": "/login?error=Please+login+to+continue"})
        if user["role"] not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"Access denied. Required: {', '.join(allowed)}")
        return user
    return role_checker
