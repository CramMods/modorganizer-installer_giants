param (
    [Parameter()] [string] $Command = "make",
    [Parameter()] [string] $SourcePath = "./src",
    [Parameter()] [string] $BuildPath = "./build",
    [Parameter()] [string] $InstallPath = [string]::Empty
)

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
    
    $UIFiles = Get-ChildItem -Path $SourcePath -Include "*.ui" -Recurse -File
    return $UIFiles | ForEach-Object -Process {
        $OutputPath = [System.IO.Path]::ChangeExtension($_.FullName, "py")
        pyuic6.exe $_.FullName -o $OutputPath
        return [PSCustomObject]@{
            Source = $_.FullName
            Output = $OutputPath
        }
    }
}

function New-Release {
    param (
        [Parameter(Mandatory)] [string] $SourcePath,
        [Parameter(Mandatory)] [string] $BuildPath
    )

    $Info = Get-ProjectInfo
    $TargetPath = Join-Path -Path $BuildPath -ChildPath $Info.Name
    Remove-Item -Path $TargetPath -Recurse -Force -ErrorAction Ignore
    New-Item -Path $TargetPath -ItemType Directory -Force | Out-Null
    Copy-Item -Path "$SourcePath/*" -Destination $TargetPath -Recurse -Exclude @("*.ui")

    $ZipName = "$($Info.Name)-$($Info.Version).zip"
    $ZipPath = Join-Path -Path $BuildPath -ChildPath $ZipName
    Remove-Item -Path $ZipPath -Force -ErrorAction Ignore
    Compress-Archive -Path $TargetPath -DestinationPath $ZipPath
}

function Install-Release {
    param (
        [Parameter(Mandatory)] [string] $BuildPath,
        [Parameter(Mandatory)] [string] $InstallPath
    )
    
    $Info = Get-ProjectInfo
    $ReleasePath = Join-Path -Path $BuildPath -ChildPath $Info.Name
    $TargetPath = Join-Path -Path $InstallPath -ChildPath $Info.Name
    Remove-Item -Path $TargetPath -Recurse -Force -ErrorAction Ignore
    New-Item -Path $TargetPath -ItemType Directory -Force | Out-Null
    Copy-Item -Path "$ReleasePath/*" -Destination $TargetPath -Recurse
}