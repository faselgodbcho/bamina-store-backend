from pathlib import Path
from environ import Env

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = Env()
env.read_env(BASE_DIR / ".env")
