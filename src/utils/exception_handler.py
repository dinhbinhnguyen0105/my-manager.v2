from src.utils.logger import Logger
import traceback
import sys

def log_exception(e: Exception) -> None:
        """Log exception with file, line, function and full traceback."""
        tb = sys.exc_info()[2]
        file_name = line_no = func_name = None
        try:
            if tb is not None:
                last = traceback.extract_tb(tb)[-1]
                file_name = last.filename
                line_no = last.lineno
                func_name = last.name
        except Exception:
            # fallback if extracting the traceback fails
            file_name = line_no = func_name = None
        logger = Logger(file_name)
        formatted = traceback.format_exc()
        meta = f"file={file_name}, line={line_no}, func={func_name}"
        logger.error(f"{type(e).__name__}: {e} ({meta})\n{formatted}")