param (
    [Parameter(Mandatory = $true)]
    [string]$Pattern,

    [Parameter(Mandatory = $true)]
    [string]$Path
)

if (Test-Path $Path) {
    if (Test-Path -Path $Path -PathType Container) {
        # If it's a directory, search recursively
        Get-ChildItem -Path $Path -Recurse -File | Select-String -Pattern $Pattern -SimpleMatch | ForEach-Object {
            Write-Host "$($_.Path):$($_.LineNumber):$($_.Line.Trim())"
        }
    }
    else {
        # If it's a file
        Select-String -Pattern $Pattern -Path $Path -SimpleMatch | ForEach-Object {
            Write-Host "$($_.LineNumber):$($_.Line.Trim())"
        }
    }
}
else {
    Write-Error "Path not found: $Path"
    exit 1
}
