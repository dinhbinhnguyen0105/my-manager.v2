# utils/profile_handlers.py

import os
import shutil
from typing import Optional, List

# Assuming Logger is available from the context of previous files
from src.utils.logger import Logger 

logger = Logger(__name__)

def create_profile_folder(profile_dir: str) -> bool:
    """
    Creates the profile directory at the specified path.
    """
    try:
        os.makedirs(profile_dir, exist_ok=True)
        logger.info(f"Profile folder created or already exists at: {profile_dir}")
        return True
    except OSError as e:
        logger.error(f"Failed to create profile folder at {profile_dir}: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during folder creation: {e}")
        return False

def remove_profile_folder(profile_dir: str) -> bool:
    """
    Deletes the profile directory and all its contents recursively.
    """
    if not os.path.exists(profile_dir):
        logger.info(f"Profile folder does not exist, nothing to remove: {profile_dir}")
        return True
    
    try:
        shutil.rmtree(profile_dir)
        logger.info(f"Profile folder and all contents successfully removed from: {profile_dir}")
        return True
    except OSError as e:
        logger.error(f"Failed to remove profile folder at {profile_dir}. It might be in use or due to permission issues: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during folder removal: {e}")
        return False