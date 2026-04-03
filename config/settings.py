"""
Compatibility shim — re-exports development settings so that any tool
still pointing at 'config.settings' continues to work.

For production, set DJANGO_SETTINGS_MODULE=config.settings.production.
"""
from config.settings.development import *  # noqa: F401, F403
