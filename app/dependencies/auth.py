from fastapi import Request, HTTPException, status

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user or "id" not in user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user