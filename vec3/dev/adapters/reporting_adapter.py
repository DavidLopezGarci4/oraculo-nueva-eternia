import json
import os
import logging
from datetime import datetime

logger = logging.getLogger("reporting_adapter")

def save_json_report(results, report_dir="logs", filename_prefix="report"):
    """
    Saves the results dictionary as a timestamped JSON report.
    """
    try:
        if not os.path.exists(report_dir):
            os.makedirs(report_dir, exist_ok=True)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(report_dir, f"{filename_prefix}_{timestamp}.json")
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        logger.info(f"📄 Report saved successfully: {report_file}")
        return report_file
    except Exception as e:
        logger.error(f"⚠️ Failed to save report: {e}")
        return None
