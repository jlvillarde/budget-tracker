from app.api.auth import router as auth_router 
from app.api.user import router as user_router
from app.api.expense import router as expense_router
from app.api.category import router as category_router


all_routes = [
    auth_router, 
    user_router,
    expense_router,
    category_router
]