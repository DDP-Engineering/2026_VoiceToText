<!--
Copyright (c) 2026 DDP Engineering
This software is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) with additional Non-Commercial restriction.
See the LICENSE and LICENSE_NC.txt files for full license details.
-->
# 2_Tools

Basic documentation for 2_Tools in the VoiceToText project.

## Repository Utilities

Gitea remains the primary development repository for this project.

- Primary remote: `origin` (Gitea)
- Optional public remote: `github` (GitHub)

The helper script below can publish a clean public snapshot to GitHub without changing the main Gitea workflow:

- `publish_github_snapshot.ps1`

Usage:

```powershell
.\2_Tools\publish_github_snapshot.ps1
```

Default behavior:

- uses `master` as the source branch
- updates local branch `public-github`
- force-pushes to remote `github` branch `master`

Optional parameters:

```powershell
.\2_Tools\publish_github_snapshot.ps1 -SourceBranch master -PublicBranch public-github -RemoteName github -RemoteBranch master
```

