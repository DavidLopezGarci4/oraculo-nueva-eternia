import os
import logging
from pathlib import Path

logger = logging.getLogger("system_adapter")

def manage_pid(pid_file=".scan_pid", action="create"):
    """
    Manages the PID file for the current process.
    """
    if action == "create":
        pid = os.getpid()
        with open(pid_file, "w") as f:
            f.write(str(pid))
        logger.debug(f"⚙️ PID file created: {pid_file} (PID: {pid})")
    elif action == "remove":
        if os.path.exists(pid_file):
            os.remove(pid_file)
            logger.debug(f"⚙️ PID file removed: {pid_file}")

def check_stop_signal(signal_file=".stop_scan"):
    """
    Checks if a stop signal file exists and returns True if it does.
    """
    if os.path.exists(signal_file):
        logger.warning(f"🛑 Stop Signal Detected via {signal_file}")
        try:
            os.remove(signal_file)
        except:
            pass
        return True
    return False

def get_root_path():
    """
    Returns the project root path.
    """
    return Path(__file__).resolve().parent.parent.parent.parent
