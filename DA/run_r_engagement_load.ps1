# Run the R engagement load script. Uses R from standard install path if Rscript is not in PATH.
# Usage: from project root, run: .\run_r_engagement_load.ps1

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot

# Try Rscript in PATH first
$rscript = Get-Command Rscript -ErrorAction SilentlyContinue
if (-not $rscript) {
    # Common Windows install path (adjust version if needed)
    $candidates = @(
        "C:\Program Files\R\R-4.5.3\bin\x64\Rscript.exe",
        "C:\Program Files\R\R-4.4.2\bin\x64\Rscript.exe",
        "C:\Program Files\R\R-4.3.3\bin\x64\Rscript.exe",
        "D:\Program Files\R\R-4.5.3\bin\x64\Rscript.exe",
        "D:\Program Files\R\R-4.4.2\bin\x64\Rscript.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) {
            $rscript = $c
            break
        }
    }
    if (-not $rscript) { throw "Rscript not found in PATH or in common R install locations. Install R or add it to PATH." }
} else {
    $rscript = $rscript.Source
}

Set-Location $projectRoot
& $rscript "r/load_engagement_to_warehouse.R"
