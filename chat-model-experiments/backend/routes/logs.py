from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import glob

router = APIRouter()

@router.delete("/delete-logs")
async def delete_logs():
    """Delete all log files in the logs folder"""
    try:
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            return JSONResponse(
                status_code=200,
                content={"message": "Logs directory does not exist", "deleted_files": 0}
            )
        
        # Find all JSON files in logs directory
        log_files = glob.glob(os.path.join(logs_dir, "*.json"))
        deleted_count = 0
        
        for file_path in log_files:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Deleted {deleted_count} log files",
                "deleted_files": deleted_count
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Error deleting logs: {str(e)}"}
        )
