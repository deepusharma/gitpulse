import pytest
import os
from unittest.mock import patch
from core.utils import load_env

# -----------------------------------------------------------------------------
# load_env
# -----------------------------------------------------------------------------

from unittest.mock import patch

def test_load_env_raises_if_key_missing():
    """load_env raises EnvironmentError if GROQ_API_KEY is not set."""
    with patch("core.utils.load_dotenv"):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(EnvironmentError):
                load_env()


def test_load_env_succeeds_with_key_present():
    """load_env passes when GROQ_API_KEY is set."""
    with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
        load_env()  # should not raise