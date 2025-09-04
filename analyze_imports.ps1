$allFiles = @()
$allImports = @()

Get-ChildItem -Path "c:\Users\Rayat\Desktop\final_project" -Recurse -Filter "*.py" | ForEach-Object {
    $relativePath = $_.FullName -replace "c:\\Users\\Rayat\\Desktop\\final_project\\", "" -replace "\\", "/"
    $relativePath = $relativePath -replace "\.py$", "" -replace "/", "."
    $allFiles += $relativePath
    
    # Get imports from this file
    Get-Content $_.FullName | Select-String "^from ([a-zA-Z_][a-zA-Z0-9_.]*)" | ForEach-Object {
        if ($_.Matches[0].Groups[1].Value -match "^[a-zA-Z_]") {
            $import = $_.Matches[0].Groups[1].Value -replace "\.", "."
            if (-not $import.StartsWith("PySide6") -and -not $import.StartsWith("google") -and -not $import.StartsWith("typing") -and -not $import.StartsWith("datetime") -and -not $import.StartsWith("json") -and -not $import.StartsWith("os") -and -not $import.StartsWith("sys") -and -not $import.StartsWith("asyncio") -and -not $import.StartsWith("qasync") -and -not $import.StartsWith("pathlib") -and -not $import.StartsWith("sqlite3") -and -not $import.StartsWith("difflib") -and -not $import.StartsWith("dataclasses") -and -not $import.StartsWith("aiohttp") -and -not $import.StartsWith("logging") -and -not $import.StartsWith("warnings") -and -not $import.StartsWith("atexit") -and -not $import.StartsWith("threading") -and -not $import.StartsWith("time") -and -not $import.StartsWith("subprocess") -and -not $import.StartsWith("shutil") -and -not $import.StartsWith("stat") -and -not $import.StartsWith("re")) {
                $allImports += $import
            }
        }
    }
}

Write-Output "=== ALL FILES (as modules) ==="
$allFiles | Sort-Object | ForEach-Object { Write-Output $_ }

Write-Output "`n=== ALL LOCAL IMPORTS ==="
$allImports | Sort-Object | Get-Unique | ForEach-Object { Write-Output $_ }

Write-Output "`n=== POTENTIALLY UNUSED FILES ==="
$allFiles | ForEach-Object {
    $file = $_
    $isImported = $false
    foreach ($import in $allImports) {
        if ($import -eq $file -or $import.StartsWith($file + ".")) {
            $isImported = $true
            break
        }
    }
    if (-not $isImported -and $file -ne "main") {
        Write-Output $file
    }
}
