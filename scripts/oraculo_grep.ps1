param (
    [string]$Pattern,
    [string]$Path = "*",
    [switch]$Recurse
)

if ($Recurse) {
    Get-ChildItem -Path $Path -Recurse -File | Select-String -Pattern $Pattern | Select-Object Path, LineNumber, Line
} else {
    Select-String -Pattern $Pattern -Path $Path | Select-Object Path, LineNumber, Line
}
