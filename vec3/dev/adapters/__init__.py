from .runtime_adapter import initialize_runtime
from .backup_adapter import create_db_backup
from .system_adapter import manage_pid, check_stop_signal, get_root_path
from .reporting_adapter import save_json_report