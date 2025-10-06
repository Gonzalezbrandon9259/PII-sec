"""
PII-sec Firewall Package
========================
Initializes configuration and logging, and exposes package-level helpers.

- Config is loaded from:
    1) ENV var PIISEC_CONFIG (if set)
    2) app/config.yaml (default)
- Logging level can be overridden via ENV var PIISEC_LOG_LEVEL (DEBUG|INFO|WARN|ERROR).

Public helpers:
    get_config()     -> dict       # current configuration
    reload_config()  -> dict       # force re-read of the config file
    get_logger(name) -> logging.Logger

Common classes (imported when available):
    Detector, Policy, Actions, AuditLogger
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # Make sure pyyaml is in requirements.txt
except Exception as e:  # pragma: no cover
    raise RuntimeError("PyYAML is required. Add 'pyyaml' to requirements.txt") from e

# -----------------------
# Version & Paths
# -----------------------
__version__ = "0.1.0"

PKG_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = PKG_DIR / "config.yaml"
ENV_CONFIG_PATH = os.getenv("PIISEC_CONFIG")
CONFIG_PATH = Path(ENV_CONFIG_PATH) if ENV_CONFIG_PATH else DEFAULT_CONFIG_PATH

# -----------------------
# Defaults (safe baseline)
# -----------------------
DEFAULT_CONFIG: Dict[str, Any] = {
    "transport": {"require_tls": True},
    "permit_list": {"recipients": []},
    "policy": {
        "actions": {
            "insecure_transport": "BLOCK",
            "contains_phi_not_permitted": "REDACT",
            "otherwise": "ALLOW",
        }
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s %(levelname)s %(name)s - %(message)s",
    },
}

_CONFIG: Dict[str, Any] = {}  # populated at import time
_LOGGING_CONFIGURED = False


# -----------------------
# Utilities
# -----------------------
def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dicts, with override taking precedence."""
    result = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _load_file_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                return {}
            return data
    except Exception:
        # If config is unreadable, fall back to defaults but keep going
        return {}


def _configure_logging(cfg: Dict[str, Any]) -> None:
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    level_name = os.getenv("PIISEC_LOG_LEVEL", cfg.get("logging", {}).get("level", "INFO"))
    level = getattr(logging, level_name.upper(), logging.INFO)
    fmt = cfg.get("logging", {}).get("format", DEFAULT_CONFIG["logging"]["format"])

    logging.basicConfig(level=level, format=fmt)
    _LOGGING_CONFIGURED = True


def reload_config() -> Dict[str, Any]:
    """Force re-read of the config file, re-apply defaults, and reconfigure logging."""
    global _CONFIG
    file_cfg = _load_file_config(CONFIG_PATH)
    _CONFIG = _deep_merge(DEFAULT_CONFIG, file_cfg)
    _configure_logging(_CONFIG)
    return _CONFIG


def get_config() -> Dict[str, Any]:
    """Return the current in-memory configuration."""
    return _CONFIG


def get_logger(name: str | None = None) -> logging.Logger:
    """Convenience accessor for a configured logger."""
    return logging.getLogger(name or "piisec")


# Initialize on import
reload_config()
logger = get_logger(__name__)
logger.debug("PII-sec package initialized with config path: %s", str(CONFIG_PATH))


# -----------------------
# Optional convenience imports (guarded to avoid circular import)
# -----------------------
# These will become available once you create the corresponding modules/classes.
# You can safely remove guards once your modules exist.

try:
    from .detector import Detector  # type: ignore
except Exception:  # pragma: no cover
    Detector = None  # type: ignore

try:
    from .policy import Policy  # type: ignore
except Exception:  # pragma: no cover
    Policy = None  # type: ignore

try:
    from .actions import Actions  # type: ignore
except Exception:  # pragma: no cover
    Actions = None  # type: ignore

try:
    from .audit import AuditLogger  # type: ignore
except Exception:  # pragma: no cover
    AuditLogger = None  # type: ignore


__all__ = [
    "__version__",
    "CONFIG_PATH",
    "get_config",
    "reload_config",
    "get_logger",
    "Detector",
    "Policy",
    "Actions",
    "AuditLogger",
]
