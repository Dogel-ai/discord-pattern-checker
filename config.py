from dynaconf import Dynaconf, Validator
from typing import Optional, List

_settings = Dynaconf(
    envvar_prefix="OBSERVER",
    environments=True,
    load_dotenv=True,
    settings_files=[
        'settings.toml',
        '.secrets.toml',
        'settings.yml',
        '.secrets.yml'
    ],
    validators=[
        # Bot settings
        Validator("log_level", is_type_of=str),
        Validator("bot_token", must_exist=True, is_type_of=str),
        # Observer settings
        Validator("observer_channels", must_exist=True, is_type_of=list, len_min=1),
        Validator("observer_patterns", must_exist=True, is_type_of=list, len_min=1),
        Validator("observer_bot_ignore", is_type_of=bool),
        # Webhook settings
        Validator("webhook_active", is_type_of=bool),
        Validator("webhook_url", is_type_of=str)
    ]
)


def log_level() -> str:
    return str(_settings.get("log_level", "INFO")).upper()


def bot_token() -> str:
    return _settings.get("bot_token")


def observer_bot_ignore() -> Optional[bool]:
    return _settings.get("bot_ignore") or None


def observer_channels() -> List[int]:
    return _settings.get("observer_channels")


def observer_patterns() -> List[str]:
    return _settings.get("observer_patterns")


def webhook_active() -> Optional[bool]:
    return _settings.get("webhook_active") or None


def webhook_url() -> Optional[bool]:
    return _settings.get("webhook_url") or None
