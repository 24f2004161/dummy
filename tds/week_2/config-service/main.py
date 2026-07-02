from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
import yaml
import os

app = FastAPI()

# Allow all origins (assignment requires browser access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

defaults = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).lower() in {"true", "1", "yes", "on"}


def coerce(config):
    config["port"] = int(config["port"])
    config["workers"] = int(config["workers"])
    config["debug"] = to_bool(config["debug"])
    config["log_level"] = str(config["log_level"])
    return config


@app.get("/effective-config")
def effective_config(set: list[str] | None = Query(default=None)):
    config = defaults.copy()

    # YAML
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml") as f:
            y = yaml.safe_load(f) or {}
            config.update(y)

    # .env
    envfile = dotenv_values(".env")

    if "NUM_WORKERS" in envfile:
        config["workers"] = envfile["NUM_WORKERS"]

    if "APP_DEBUG" in envfile:
        config["debug"] = envfile["APP_DEBUG"]

    if "APP_API_KEY" in envfile:
        config["api_key"] = envfile["APP_API_KEY"]

    # OS env (highest before CLI)
    if "APP_DEBUG" in os.environ:
        config["debug"] = os.environ["APP_DEBUG"]

    if "APP_LOG_LEVEL" in os.environ:
        config["log_level"] = os.environ["APP_LOG_LEVEL"]

    if "APP_API_KEY" in os.environ:
        config["api_key"] = os.environ["APP_API_KEY"]

    # CLI overrides
    if set:
        for item in set:
            key, value = item.split("=", 1)
            config[key] = value

    config = coerce(config)

    # Secret masking
    config["api_key"] = "****"

    return config
