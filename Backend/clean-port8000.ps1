# clean-port8000.ps1
param([switch]$WhatIf)

$port = 8000

function Get-FocusFlowPortPids {
    $connections = @(Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue)
    return @($connections | Where-Object { $_.OwningProcess -gt 0 } | Select-Object -ExpandProperty OwningProcess -Unique)
}

function Get-ProcessTreePids {
    param([int[]]$RootPids)

    $all = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
    $found = [System.Collections.Generic.HashSet[int]]::new()
    $queue = [System.Collections.Generic.Queue[int]]::new()

    foreach ($root in $RootPids) {
        if ($found.Add([int]$root)) {
            $queue.Enqueue([int]$root)
        }
    }

    while ($queue.Count -gt 0) {
        $parent = $queue.Dequeue()
        foreach ($process in $all) {
            if ($process.ParentProcessId -eq $parent -and $found.Add([int]$process.ProcessId)) {
                $queue.Enqueue([int]$process.ProcessId)
            }
        }
    }

    return @($found)
}

function Get-OrphanedServerPids {
    $patterns = @('main:app', 'uvicorn', '--multiprocessing-fork', 'spawn_main')
    $processes = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        if ($_.Name -notmatch 'python') {
            return $false
        }
        $commandLine = $_.CommandLine
        if (-not $commandLine) {
            return $false
        }
        foreach ($pattern in $patterns) {
            if ($commandLine -like "*$pattern*") {
                return $true
            }
        }
        return $false
    })
    return @($processes | Select-Object -ExpandProperty ProcessId)
}

$portPids = @(Get-FocusFlowPortPids)
$targets = @()
$targets += @(Get-ProcessTreePids -RootPids $portPids)
$targets += @(Get-OrphanedServerPids)
$targets = @($targets | Where-Object { $_ -gt 0 -and $_ -ne $PID } | Sort-Object -Unique)

if ($targets.Count -eq 0) {
    Write-Host "No FocusFlow server process is using port $port."
    exit 0
}

Write-Host "Found PID(s) $($targets -join ', ') to stop for port $port."

foreach ($targetPid in $targets) {
    $process = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "  PID $targetPid : $($process.ProcessName) - $($process.Path)"
    } else {
        Write-Host "  PID $targetPid : no longer running"
    }
    if ($WhatIf) {
        continue
    }
    Stop-Process -Id $targetPid -Force -ErrorAction SilentlyContinue
}

if ($WhatIf) {
    Write-Host "WhatIf: no processes were stopped."
    exit 0
}

Start-Sleep -Seconds 1
$remaining = @(Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue)
if ($remaining.Count -gt 0) {
    $owners = ($remaining | Select-Object -ExpandProperty OwningProcess -Unique) -join ', '
    Write-Warning "Port $port is still in use by PID(s) $owners. Investigate manually."
} else {
    Write-Host "Port $port is now free."
}
