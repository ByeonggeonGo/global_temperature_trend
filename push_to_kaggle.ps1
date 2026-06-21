param(
  [switch]$CreateDataset,
  [switch]$VersionDataset,
  [switch]$PushNotebook
)

$ErrorActionPreference = "Stop"

Write-Host "Checking Kaggle authentication..."
python -m kaggle config view | Out-Host

if ($CreateDataset) {
  python -m kaggle datasets create -p kaggle_dataset
}

if ($VersionDataset) {
  python -m kaggle datasets version -p kaggle_dataset -m "Update global temperature source samples"
}

if ($PushNotebook) {
  python -m kaggle kernels push -p kaggle_code
}

if (-not ($CreateDataset -or $VersionDataset -or $PushNotebook)) {
  Write-Host "No action selected. Use -CreateDataset, -VersionDataset, and/or -PushNotebook."
}
