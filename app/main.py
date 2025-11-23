from fastapi import FastAPI
from app.database import engine, Base
from app.routers import user as user_router
from app.routers import user_role as role_router
from app.routers import category as category_router
from app.routers import summary as summary_router
from app.routers import comment as comment_router
from app.routers import auth as auth_router
from app.routers import content_section as sections_router
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

# CORS
allowed_origins = ["*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(note_router.router)
app.include_router(reading_history_router.router)
app.include_router(vocabulary_router.router)
app.include_router(recommendation_router.router)
app.include_router(rating_router.router)
app.include_router(auth_router.router)
app.include_router(sections_router.router)
