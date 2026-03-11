# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.
#
# Publish script for optional GitHub snapshot updates.
# Keeps Gitea as the primary repository and force-pushes a clean
# source snapshot from the main development branch to GitHub.
#
# Usage:
#   .\2_Tools\publish_github_snapshot.ps1
#   .\2_Tools\publish_github_snapshot.ps1 -SourceBranch master
#   .\2_Tools\publish_github_snapshot.ps1 -RemoteName github -PublicBranch public-github -RemoteBranch master

param(
    [string]$SourceBranch = "master",
    [string]$PublicBranch = "public-github",
    [string]$RemoteName = "github",
    [string]$RemoteBranch = "master"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -----------------------------------------------------------------------------
# Resolve paths
# -----------------------------------------------------------------------------
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & git -C $repoRoot @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git -C `"$repoRoot`" $($Arguments -join ' ')"
    }
}

Write-Host "========================================"
Write-Host "Publish Optional GitHub Snapshot"
Write-Host "========================================"
Write-Host "[publish] Repository root: $repoRoot"
Write-Host "[publish] Source branch:   $SourceBranch"
Write-Host "[publish] Public branch:   $PublicBranch"
Write-Host "[publish] Remote target:   $RemoteName/$RemoteBranch"

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
$statusOutput = (& git -C $repoRoot status --porcelain)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to read git status."
}
if (-not [string]::IsNullOrWhiteSpace(($statusOutput | Out-String))) {
    throw "Working tree is not clean. Commit or stash changes before publishing."
}

$currentBranch = (& git -C $repoRoot branch --show-current).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Unable to detect current branch."
}

$sourceExists = (& git -C $repoRoot rev-parse --verify $SourceBranch 2>$null)
if ($LASTEXITCODE -ne 0) {
    throw "Source branch not found: $SourceBranch"
}

$remoteExists = (& git -C $repoRoot remote)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to read configured remotes."
}
if ($remoteExists -notcontains $RemoteName) {
    throw "Remote not found: $RemoteName"
}

$publicBranchExists = $true
& git -C $repoRoot rev-parse --verify $PublicBranch 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    $publicBranchExists = $false
}

try {
    # -------------------------------------------------------------------------
    # Prepare public branch snapshot
    # -------------------------------------------------------------------------
    if ($publicBranchExists) {
        Invoke-Git -Arguments @("checkout", $PublicBranch)
    }
    else {
        Invoke-Git -Arguments @("checkout", "--orphan", $PublicBranch)
    }

    $trackedFiles = (& git -C $repoRoot ls-files)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to enumerate tracked files."
    }
    if (-not [string]::IsNullOrWhiteSpace(($trackedFiles | Out-String))) {
        Invoke-Git -Arguments @("rm", "-r", "--quiet", "--ignore-unmatch", ".")
    }

    Invoke-Git -Arguments @("checkout", $SourceBranch, "--", ".")
    Invoke-Git -Arguments @("add", ".")

    $hasChanges = (& git -C $repoRoot status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect staged snapshot changes."
    }

    if (-not [string]::IsNullOrWhiteSpace(($hasChanges | Out-String))) {
        Invoke-Git -Arguments @("commit", "-m", "Public snapshot update")
    }
    else {
        Write-Host "[publish] No content changes detected. Reusing current public snapshot commit."
    }

    # -------------------------------------------------------------------------
    # Push snapshot
    # -------------------------------------------------------------------------
    Invoke-Git -Arguments @("push", $RemoteName, "$PublicBranch`:$RemoteBranch", "--force")
    Write-Host "[publish] GitHub snapshot updated successfully."
}
finally {
    if (-not [string]::IsNullOrWhiteSpace($currentBranch)) {
        & git -C $repoRoot checkout $currentBranch | Out-Null
    }
}
