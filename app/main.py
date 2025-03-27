from app.core.app_factory import create_app
from app.deps.settings import get_settings

settings = get_settings()
app = create_app(settings)
