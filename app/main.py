from fastapi import FastAPI
from app.database import engine, Base
from app.routers import user as user_router
from app.routers import user_role as role_router
from app.routers import category as category_router
from app.routers import summary as summary_router
from app.routers import comment as comment_router
from app.routers import auth as auth_router
from app.routers import author as author_router
from app.routers import publisher as publisher_router
from app.routers import book as book_router
from app.routers import order as order_router
from app.routers import order_detail as order_detail_router
from app.routers import content_section as content_section_router
from app.routers import admin_comment as admin_comment_router
from app.routers import cart as cart_router
from app.routers import cart_item as cart_item_router
from app.routers import favourite as favourite_router
from app.routers import payment as payment_router
from fastapi.middleware.cors import CORSMiddleware

# Tự động import tất cả modules trong app.models để đăng ký models vào Base.metadata
def _import_all_models() -> None:
    import importlib
    import pkgutil
    import pathlib

    package_name = "app.models"
    pkg = importlib.import_module(package_name)
    pkg_path = pathlib.Path(pkg.__file__).parent

    for module_info in pkgutil.iter_modules([str(pkg_path)]):
        if module_info.ispkg:
            continue
        importlib.import_module(f"{package_name}.{module_info.name}")


app = FastAPI(
    title="Book Learning API",
    version="1.0.0",
    description="Backend for Book Learning App"
)

#Turn on CORS
origins = [
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # hoặc ["*"] để cho phép tất cả
    allow_credentials=True,
    allow_methods=["*"],            # Cho phép tất cả các phương thức (GET, POST, PUT, DELETE,...)
    allow_headers=["*"],            # Cho phép tất cả các header
)

@app.on_event("startup")
def on_startup_create_tables():
    # Import tất cả models và tạo bảng khi ứng dụng khởi động
    _import_all_models()
    Base.metadata.create_all(bind=engine)
    try:
        from sqlalchemy import inspect
        tables = inspect(engine).get_table_names()
        print(f"[DB] Initialized tables: {tables}")
    except Exception:
        pass


@app.get("/")
def root():
    return {"message": "🚀 Database tables created!"}

# Mount routers
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(role_router.router)
app.include_router(category_router.router)
app.include_router(author_router.router)
app.include_router(publisher_router.router)
app.include_router(book_router.router)
app.include_router(order_router.router)
app.include_router(order_detail_router.router)
app.include_router(cart_router.router)
app.include_router(cart_item_router.router)
app.include_router(summary_router.router)
app.include_router(content_section_router.router)
app.include_router(comment_router.router)
app.include_router(admin_comment_router.router)
app.include_router(favourite_router.router)
app.include_router(payment_router.router)
