# Re-export submodules so `from app import models` has attributes like `models.user`
from . import user  # noqa: F401
from . import user_role  # noqa: F401
from . import category  # noqa: F401
from . import summary  # noqa: F401
from . import comment  # noqa: F401
from . import note  # noqa: F401
from . import reading_history  # noqa: F401
from . import vocabulary  # noqa: F401
from . import recommendation  # noqa: F401
from . import rating  # noqa: F401

__all__ = [
    "user",
    "user_role",
    "category",
    "summary",
    "comment",
    "note",
    "reading_history",
    "vocabulary",
    "recommendation",
    "rating",
]


