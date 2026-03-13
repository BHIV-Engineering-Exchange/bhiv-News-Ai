param(
    [string]$PythonExe = "python",
    [string]$MonitorScript = "c:\Users\user11\Desktop\News AI\monitor_backend.py",
    [int]$Interval = 30
)

# Creates a scheduled task that runs the monitor at system startup.
$taskName = "NewsAI Monitor"
$action = "$PythonExe \"$MonitorScript\" --interval $Interval"

Write-Host "Creating scheduled task '$taskName' to run: $action"
schtasks /Create /TN $taskName /TR $action /SC ONSTART /RL HIGHEST /F
Write-Host "Task created. To remove, run uninstall_monitor_task.ps1"
