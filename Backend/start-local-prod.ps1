param([switch]$Reload)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (-not (Test-Path (Join-Path $PSScriptRoot ".env"))) {
    throw "Backend/.env is missing. Create it from .env.example and set your local database and JWT settings."
}

$jwtSecret = $env:JWT_SECRET
if (-not $jwtSecret) {
    foreach ($line in Get-Content (Join-Path $PSScriptRoot ".env")) {
        if ($line -match '^\s*JWT_SECRET\s*=\s*(.*?)\s*$') {
            $jwtSecret = $Matches[1].Trim('"').Trim("'")
            break
        }
    }
}
if (-not $jwtSecret -or $jwtSecret.Length -lt 32 -or $jwtSecret -eq "replace-with-a-long-random-secret") {
    throw "Set a private JWT_SECRET of at least 32 characters in Backend/.env before starting the local production-style API."
}

$postgres = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $postgres) {
    throw "PostgreSQL is not reachable at localhost:5432. Start your local PostgreSQL service first."
}

$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
    throw "Docker CLI is not available on PATH. Install Docker Desktop, then open a new terminal."
}

docker info *> $null
$engineRunning = $LASTEXITCODE -eq 0
if (-not $engineRunning) {
    $dockerDesktop = Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe"
    if (-not (Test-Path $dockerDesktop)) {
        throw "Docker Desktop was not found at the default install path: $dockerDesktop"
    }

    if (-not (Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue)) {
        Start-Process -FilePath $dockerDesktop
    }

    Write-Host "Waiting for Docker Desktop to start..."
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        Start-Sleep -Seconds 2
        docker info *> $null
        if ($LASTEXITCODE -eq 0) {
            $engineRunning = $true
            break
        }
    }
}

if (-not $engineRunning) {
    throw "Docker Desktop did not become ready within two minutes. Open it and check its status, then retry."
}

$uvicornArgs = @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000")
if ($Reload) {
    $uvicornArgs += "--reload"
}

$python = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python was not found. Create the Backend virtual environment and install requirements.txt."
    }
    $python = $pythonCommand.Source
}

# Bind uvicorn and every process it spawns to a job object. Closing the job
# handle terminates the whole tree, including when this script is closed
# abruptly (terminal closed, killed, or an unhandled error).
$jobTypeDefinition = @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;

public static class FocusFlowProcessJob
{
    [StructLayout(LayoutKind.Sequential)]
    private struct JOBOBJECT_BASIC_LIMIT_INFORMATION
    {
        public long PerProcessUserTimeLimit;
        public long PerJobUserTimeLimit;
        public uint LimitFlags;
        public UIntPtr MinimumWorkingSetSize;
        public UIntPtr MaximumWorkingSetSize;
        public uint ActiveProcessLimit;
        public UIntPtr Affinity;
        public uint PriorityClass;
        public uint SchedulingClass;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct IO_COUNTERS
    {
        public ulong ReadOperationCount;
        public ulong WriteOperationCount;
        public ulong OtherOperationCount;
        public ulong ReadTransferCount;
        public ulong WriteTransferCount;
        public ulong OtherTransferCount;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION
    {
        public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
        public IO_COUNTERS IoInfo;
        public UIntPtr ProcessMemoryLimit;
        public UIntPtr JobMemoryLimit;
        public UIntPtr PeakProcessMemoryUsed;
        public UIntPtr PeakJobMemoryUsed;
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr CreateJobObject(IntPtr lpJobAttributes, string lpName);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetInformationJobObject(IntPtr hJob, int JobObjectInfoClass, IntPtr lpJobObjectInfo, uint cbJobObjectInfoLength);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool AssignProcessToJobObject(IntPtr hJob, IntPtr hProcess);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool CloseHandle(IntPtr hObject);

    public static IntPtr Create()
    {
        IntPtr job = CreateJobObject(IntPtr.Zero, null);
        if (job == IntPtr.Zero)
            throw new Win32Exception(Marshal.GetLastWin32Error());

        var info = new JOBOBJECT_EXTENDED_LIMIT_INFORMATION();
        info.BasicLimitInformation.LimitFlags = 0x2000; // JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        int length = Marshal.SizeOf(typeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION));
        IntPtr buffer = Marshal.AllocHGlobal(length);
        try
        {
            Marshal.StructureToPtr(info, buffer, false);
            if (!SetInformationJobObject(job, 9, buffer, (uint)length))
                throw new Win32Exception(Marshal.GetLastWin32Error());
        }
        finally
        {
            Marshal.FreeHGlobal(buffer);
        }
        return job;
    }

    public static bool Assign(IntPtr job, IntPtr processHandle)
    {
        return AssignProcessToJobObject(job, processHandle);
    }

    public static void Close(IntPtr job)
    {
        if (job != IntPtr.Zero)
            CloseHandle(job);
    }
}
'@
Add-Type -TypeDefinition $jobTypeDefinition

$uvicornStartInfo = New-Object System.Diagnostics.ProcessStartInfo
$uvicornStartInfo.FileName = $python
$uvicornStartInfo.Arguments = ($uvicornArgs | ForEach-Object { '"' + $_ + '"' }) -join ' '
$uvicornStartInfo.WorkingDirectory = $PSScriptRoot
$uvicornStartInfo.UseShellExecute = $false
$uvicornStartInfo.CreateNoWindow = $false

$env:FOCUSFLOW_LAUNCHER_PID = "$PID"

$uvicornProcess = New-Object System.Diagnostics.Process
$uvicornProcess.StartInfo = $uvicornStartInfo

$job = [IntPtr]::Zero
$jobAssigned = $false
$LASTEXITCODE = 0

try {
    $job = [FocusFlowProcessJob]::Create()
    [void]$uvicornProcess.Start()
    $jobAssigned = [FocusFlowProcessJob]::Assign($job, $uvicornProcess.Handle)
    if (-not $jobAssigned) {
        Write-Warning "Could not assign uvicorn to a job object; only the direct child will be stopped on exit."
    }

    $uvicornProcess.WaitForExit()
    $LASTEXITCODE = $uvicornProcess.ExitCode
}
finally {
    if (-not $jobAssigned -and $uvicornProcess -and -not $uvicornProcess.HasExited) {
        Write-Host "Stopping uvicorn process ($($uvicornProcess.Id))..."
        Stop-Process -Id $uvicornProcess.Id -Force -ErrorAction SilentlyContinue
    }
    [FocusFlowProcessJob]::Close($job)
}

Remove-Item Env:FOCUSFLOW_LAUNCHER_PID -ErrorAction SilentlyContinue

Start-Sleep -Milliseconds 500
$remaining = @(Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue)
if ($remaining.Count -gt 0) {
    $owners = ($remaining | Select-Object -ExpandProperty OwningProcess -Unique) -join ', '
    Write-Warning "Port 8000 is still in use by PID(s) $owners. Run ./clean-port8000.ps1 to clear it."
}

exit $LASTEXITCODE
