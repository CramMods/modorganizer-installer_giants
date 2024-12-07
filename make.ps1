param (
    [Parameter()] [string] $Command = "make",
    [Parameter()] [string] $SourcePath = "./src",
    [Parameter()] [string] $BuildPath = "./build",
    [Parameter()] [string] $InstallPath = [string]::Empty
)

function Get-ProjectInfo {
    $ProjectFile = "./pyproject.toml"
    $FileContent = Get-Content -Path $ProjectFile

    $Info = [PSCustomObject]@{
        Name = ""
        Version = ""
    }

    $SectionTitles = $FileContent | Select-String -Pattern "^\[(?<title>.+?)\]$"
    for ($Index = 0; $Index -lt $SectionTitles.Length; $Index++) {
        $Section = $SectionTitles[$Index]
        $Title = $Section.Matches[0].Groups["title"].Value
        
        if ($Title -eq "tool.poetry") {
            $StartLine = $Section.LineNumber
            $EndLine = if (($Index + 1) -lt $SectionTitles.Length) {
                $SectionTitles[$Index + 1].LineNumber - 1 - 1
            } else {
                $FileContent.Length - 1
            }

            $SectionContent = $FileContent[$StartLine..$EndLine] 
            $SectionItems = $SectionContent | Select-String -Pattern "(?<key>.+?)\s*=\s*(?<value>.+)"
            for ($ItemIndex = 0; $ItemIndex -lt $SectionItems.Length; $ItemIndex++) {
                $Item = $SectionItems[$ItemIndex]
                $Key = $Item.Matches[0].Groups["key"].Value
                $Value = $Item.Matches[0].Groups["value"].Value

                switch ($Key) {
                    "name" { $Info.Name = $Value.Trim("`"") }
                    "version" { $Info.Version = $Value.Trim("`"") }
                    Default {}
                }
            }
        }
    }
    return $Info
}

function Update-UI {
    param (
        [Parameter(Mandatory)] [string] $SourcePath
    )

    Write-Host "Building .ui files to .py... " -NoNewline
    $UIFiles = Get-ChildItem -Path $SourcePath -Include "*.ui" -Recurse -File
    $UIFiles | ForEach-Object -Process {
        $OutputPath = [System.IO.Path]::ChangeExtension($_.FullName, "py")
        pyuic6.exe $_.FullName -o $OutputPath
        Write-Host "`n - $($_.FullName) -> $OutputPath" -ForegroundColor Magenta
    }
    Write-Host "done" -ForegroundColor Green
    Write-Host ""
}

function New-Release {
    param (
        [Parameter(Mandatory)] [string] $SourcePath,
        [Parameter(Mandatory)] [string] $BuildPath
    )

    Write-Host "Copying files to release... " -NoNewline
    $Info = Get-ProjectInfo
    $TargetPath = Join-Path -Path $BuildPath -ChildPath $Info.Name
    Remove-Item -Path $TargetPath -Recurse -Force -ErrorAction Ignore
    New-Item -Path $TargetPath -ItemType Directory -Force | Out-Null
    Copy-Item -Path "$SourcePath/*" -Destination $TargetPath -Recurse -Exclude @("*.ui")
    Write-Host "done" -ForegroundColor Green
    Write-Host $TargetPath -ForegroundColor Magenta
    Write-Host ""

    Write-Host "Creating zip for release... " -NoNewline
    $ZipName = "$($Info.Name)-$($Info.Version).zip"
    $ZipPath = Join-Path -Path $BuildPath -ChildPath $ZipName
    Remove-Item -Path $ZipPath -Force -ErrorAction Ignore
    Compress-Archive -Path $TargetPath -DestinationPath $ZipPath
    Write-Host "done" -ForegroundColor Green
    Write-Host $ZipPath -ForegroundColor Magenta
    Write-Host ""
}

function Install-Release {
    param (
        [Parameter(Mandatory)] [string] $BuildPath,
        [Parameter(Mandatory)] [string] $InstallPath
    )
    
    Write-Host "Installing release... " -NoNewline
    $Info = Get-ProjectInfo
    $ReleasePath = Join-Path -Path $BuildPath -ChildPath $Info.Name
    $TargetPath = Join-Path -Path $InstallPath -ChildPath $Info.Name
    Remove-Item -Path $TargetPath -Recurse -Force -ErrorAction Ignore
    New-Item -Path $TargetPath -ItemType Directory -Force | Out-Null
    Copy-Item -Path "$ReleasePath/*" -Destination $TargetPath -Recurse
    Write-Host "done" -ForegroundColor Green
    Write-Host $InstallPath -ForegroundColor Magenta
    Write-Host ""
}

switch ($Command) {
    "make" {
        Update-UI -SourcePath $SourcePath
    }
    "release" {
        Update-UI -SourcePath $SourcePath
        New-Release -SourcePath $SourcePath -BuildPath $BuildPath
    }
    "install" {
        Update-UI -SourcePath $SourcePath
        New-Release -SourcePath $SourcePath -BuildPath $BuildPath
        Install-Release -BuildPath $BuildPath -InstallPath $InstallPath
    }
    default { throw [System.ArgumentException]::new("Unknown command: `"$Command`"") }
}