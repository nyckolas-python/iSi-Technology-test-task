from pathlib import Path

from environ import Env
from split_settings.tools import include, optional

config = Env(
    DEBUG=(bool, False),
)
DEBUG = config('DEBUG')

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

config.read_env(BASE_DIR / '.env')

_env = config('ENV')
_base_settings = (
    "components/_base.py",
    "components/*.py",
    'environments/{0}.py'.format(_env),
    # Optionally override some settings:
    optional('environments/local.py'),
)

# Include settings:
include(*_base_settings)
