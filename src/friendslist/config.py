import tomllib
import os

ENV = os.getenv("APP_ENV", "dev")

CONFIG_FILE = "config.test.toml" if ENV == "test" else "config.toml"

with open(CONFIG_FILE, "rb") as f:
    config = tomllib.load(f)
