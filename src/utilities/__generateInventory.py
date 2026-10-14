import datetime
import os
import subprocess

C_TARGET_DIR = "eNuts"
C_DOCS_DIR = os.path.join(C_TARGET_DIR, ".docs")
C_OUTPUT_FILE = os.path.join(C_DOCS_DIR, "inventory.md")

# --- Customization Controls ---
C_MAX_COMMITS = 5  # Limits how many recent commits are included in the history section
C_EXCLUDED_EXTENSIONS = {
    ".log",
    ".tmp",
    ".cache",
    ".DS_Store",
}  # File extensions to filter out
# ------------------------------


def _runGitCommand(commandList):
    """Executes a git command and returns standard output lines."""
    try:
        lResult = subprocess.run(
            commandList,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return lResult.stdout.strip().split("\n")
    except Exception as lErr:
        print(f"Git command error: {lErr}")
        return []


def _shouldIncludeFile(filePath):
    """Checks if a file path has an excluded extension."""
    _, lExt = os.path.splitext(filePath)
    return lExt.lower() not in C_EXCLUDED_EXTENSIONS


def _parseChangeHistory(commitLimit):
    """Retrieves recent push/commit history up to commitLimit and formats detailed change logs."""
    lGitLogRaw = _runGitCommand(
        [
            "git",
            "log",
            "-n",
            str(commitLimit),
            "--name-status",
            "--pretty=format:COMMIT_START|%h|%an|%ad|%s",
            "--date=short",
        ]
    )

    lHistoryEntries = []
    lCurrentCommit = None

    for lLine in lGitLogRaw:
        if not lLine:
            continue
        if lLine.startswith("COMMIT_START|"):
            _, lHash, lAuthor, lDate, lSubject = lLine.split("|", 4)
            lCurrentCommit = {
                "hash": lHash,
                "author": lAuthor,
                "date": lDate,
                "subject": lSubject,
                "changes": [],
            }
            lHistoryEntries.append(lCurrentCommit)
        elif lCurrentCommit:
            lParts = lLine.split("\t")
            if len(lParts) >= 2:
                lStatus = lParts[0][0]
                lFilePath = lParts[1]

                if not _shouldIncludeFile(lFilePath):
                    continue

                if lStatus == "A":
                    lChangesText = f"New file: `{lFilePath}`"
                elif lStatus == "M":
                    lChangesText = f"Modified: `{lFilePath}`"
                elif lStatus == "D":
                    lChangesText = f"Deleted: `{lFilePath}`"
                elif lStatus == "R" and len(lParts) >= 3:
                    lNewPath = lParts[2]
                    if _shouldIncludeFile(lNewPath):
                        lChangesText = f"Renamed/Moved: `{lFilePath}` -> `{lNewPath}`"
                    else:
                        continue
                else:
                    lChangesText = f"Updated: `{lFilePath}`"

                lCurrentCommit["changes"].append(lChangesText)

    return lHistoryEntries


def generateInventory():
    os.makedirs(C_DOCS_DIR, exist_ok=True)
    lCurrentTime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    lLines = [
        "# eNuts Asset & Directory Inventory",
        f"*Auto-generated on: {lCurrentTime}*",
        "",
        "## Current Directory Structure",
        "",
    ]

    for lRoot, lDirs, lFiles in os.walk(C_TARGET_DIR):
        lFilteredFiles = [lF for lF in lFiles if _shouldIncludeFile(lF)]
        lLevel = lRoot.replace(C_TARGET_DIR, "").count(os.sep)
        lIndent = "  " * lLevel
        lLines.append(f"{lIndent}- **{os.path.basename(lRoot)}/**")
        lSubIndent = "  " * (lLevel + 1)
        for lFile in sorted(lFilteredFiles):
            lLines.append(f"{lSubIndent}- {lFile}")

    lLines.extend(["", "---", "", "## Push & Change History", ""])

    lHistory = _parseChangeHistory(C_MAX_COMMITS)
    if not lHistory:
        lLines.append("*No recent commit history found.*")
    else:
        for lEntry in lHistory:
            lLines.append(f"### Commit `{lEntry['hash']}` — {lEntry['subject']}")
            lLines.append(
                f"**Author:** {lEntry['author']} | **Date:** {lEntry['date']}"
            )
            lLines.append("")
            if lEntry["changes"]:
                for lChange in lEntry["changes"]:
                    lLines.append(f"* {lChange}")
            else:
                lLines.append(
                    "* No structural file changes recorded (or filtered out)."
                )
            lLines.append("")

    with open(C_OUTPUT_FILE, "w", encoding="utf-8") as lFileHandle:
        lFileHandle.write("\n".join(lLines))

    print(f"Successfully generated {C_OUTPUT_FILE}")


if __name__ == "__main__":
    generateInventory()
