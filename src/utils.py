import os
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)


# 1. load .env file using load_dotenv()
# 2. define required keys — just GROQ_API_KEY for now
# 3. check each required key is present in os.environ
# 4. if any missing — log each missing key, raise EnvironmentError
# 5. log success

def load_env():
    """
    Load the .env file and check for required keys
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        EnvironmentError: If any required keys are missing
    """
    
    load_dotenv()   
    required_keys = ["GROQ_API_KEY"]
    missing_keys = [key for key in required_keys if key not in os.environ]
    if missing_keys:
        for key in missing_keys:
            logger.error("Missing required environment variable: %s", key)
        raise EnvironmentError("Missing required environment variables: %s" % ", ".join(missing_keys))
    logger.debug("Environment variables loaded successfully")
    


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.debug("utils.py: __main__")
    