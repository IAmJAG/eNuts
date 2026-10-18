import ast
import datetime
import os
import subprocess

C_TARGET_DIR = "."
C_DOCS_DIR = os.path.join(C_TARGET_DIR, ".docs")
C_OUTPUT_FILE = os.path.join(C_DOCS_DIR, "inventory.md")

# --- Customization Controls ---
C_MAX_COMMITS = 10
C_EXCLUDED_EXTENSIONS = {
    ".log",
    ".tmp",
    ".cache",
    ".DS_Store",
    ".pyc",
    ".f",
    ".ff",
    ".fff",
    ".ffff",
    ".gitignore",
}  # File extensions to filter out

C_EXCLUDED_DIRECTORIES = {
    ".git",
    ".docs",
    "__pycache__",
    ".idea",
    ".vscode",
    "objects",
    ".github",
    ".kilo",
    "LOGS",
}  # Directories to skip entirely during inventory scanning

C_EXCLUDED_FILES = {
    "__init__.py",
}  # Specific filenames to exclude from the inventory

C_EXCLUDED_VARIABLES = {
    "__all__",
}  # Repetitive or standard module variables/constants to omit from inventory
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
    """Checks if a file path has an excluded extension or filename."""
    lBaseName = os.path.basename(filePath)
    if lBaseName in C_EXCLUDED_FILES:
        return False
    _, lExt = os.path.splitext(filePath)
    return lExt.lower() not in C_EXCLUDED_EXTENSIONS


def _findDocPath(filePath):
    """Maps a source file path to its optional documentation path under .docs/."""
    lNormPath = os.path.normpath(filePath)
    lParts = list(os.path.split(lNormPath))

    lDocParts = []
    for lPart in lParts:
        if lPart == "src":
            continue
        lDocParts.append(lPart)

    if lDocParts and lDocParts[0] == ".":
        lDocParts.pop(0)

    if not lDocParts:
        return ""

    lFileName = lDocParts[-1]
    lFileStem, _ = os.path.splitext(lFileName)
    if lFileStem.startswith("__"):
        lFileStem = lFileStem[2:]
    elif lFileStem.startswith("_"):
        lFileStem = lFileStem[1:]

    lDocParts[-1] = f"{lFileStem}.md"
    lCandidateDocPath = (
        os.path.join(C_DOCS_DIR, *lDocParts[1:])
        if len(lDocParts) > 1
        else os.path.join(C_DOCS_DIR, f"{lFileStem}.md")
    )

    if os.path.exists(lCandidateDocPath):
        return os.path.relpath(lCandidateDocPath, C_TARGET_DIR).replace("\\", "/")
    return ""


def _parsePythonFile(filePath):
    """Parses a Python file using AST to extract classes, functions, constants, and global variables."""
    lComponents = {"classes": [], "functions": [], "constants": [], "globals": []}

    try:
        with open(filePath, "r", encoding="utf-8") as lFile:
            lTree = ast.parse(lFile.read(), filename=filePath)
    except Exception:
        return lComponents

    for lNode in lTree.body:
        if isinstance(lNode, ast.ClassDef):
            lComponents["classes"].append(lNode.name)
        elif isinstance(lNode, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lComponents["functions"].append(lNode.name)
        elif isinstance(lNode, ast.Assign):
            for lTarget in lNode.targets:
                if isinstance(lTarget, ast.Name):
                    lName = lTarget.id
                    if lName in C_EXCLUDED_VARIABLES:
                        continue
                    if lName.startswith("C_") or lName.isupper():
                        lComponents["constants"].append(lName)
                    elif lName.startswith("G_"):
                        lComponents["globals"].append(lName)
                    else:
                        lComponents["globals"].append(lName)
        elif isinstance(lNode, ast.AnnAssign):
            if isinstance(lNode.target, ast.Name):
                lName = lNode.target.id
                if lName in C_EXCLUDED_VARIABLES:
                    continue
                if lName.startswith("C_") or lName.isupper():
                    lComponents["constants"].append(lName)
                else:
                    lComponents["globals"].append(lName)

    return lComponents


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
                "files": [],
            }
            lHistoryEntries.append(lCurrentCommit)
        elif lCurrentCommit:
            lParts = lLine.split("\t")
            if len(lParts) >= 2:
                lStatus = lParts[0][0]
                lFilePath = lParts[1]
                if not _shouldIncludeFile(lFilePath):
                    continue
                if lStatus == "R" and len(lParts) >= 3:
                    lFilePath = f"{lParts[1]} -> {lParts[2]}"
                lCurrentCommit["files"].append(lFilePath)

    return lHistoryEntries


def _buildTreeLines(startDir, prefix=""):
    """Recursively builds pure tree structure lines."""
    lTreeLines = []
    try:
        lEntries = sorted(os.listdir(startDir))
    except OSError:
        return lTreeLines

    lValidEntries = []
    for lEntry in lEntries:
        lFullPath = os.path.join(startDir, lEntry)
        if os.path.isdir(lFullPath):
            if lEntry in C_EXCLUDED_DIRECTORIES:
                continue
            lValidEntries.append((lEntry, True))
        else:
            if not _shouldIncludeFile(lEntry):
                continue
            lValidEntries.append((lEntry, False))

    for lIdx, (lName, lIsDir) in enumerate(lValidEntries):
        lIsLast = lIdx == len(lValidEntries) - 1
        lConnector = "└── " if lIsLast else "├── "
        lFullPath = os.path.join(startDir, lName)

        if lIsDir:
            lTreeLines.append(f"{prefix}{lConnector}{lName}/")
            lExtension = "    " if lIsLast else "│   "
            lTreeLines.extend(_buildTreeLines(lFullPath, prefix + lExtension))
        else:
            lTreeLines.append(f"{prefix}{lConnector}{lName}")

    return lTreeLines


def _buildFileDetailsLines():
    """Builds the file details section matching the requested categorized format with proper indentation."""
    lDetailLines = []

    for lRoot, lDirs, lFiles in os.walk(C_TARGET_DIR):
        lDirs[:] = [lDir for lDir in lDirs if lDir not in C_EXCLUDED_DIRECTORIES]
        lFilteredFiles = sorted(
            [
                lF
                for lF in lFiles
                if _shouldIncludeFile(os.path.join(lRoot, lF)) and lF.endswith(".py")
            ]
        )

        if not lFilteredFiles:
            continue

        lRelRoot = os.path.relpath(lRoot, C_TARGET_DIR)
        lDirPath = "." if lRelRoot == "." else lRelRoot.replace(os.sep, "/")

        # Directory path header
        lDetailLines.append(f"{lDirPath}:")

        for lFile in lFilteredFiles:
            lFullPath = os.path.join(lRoot, lFile)
            lDocPath = _findDocPath(lFullPath)

            # File entry
            lDetailLines.append(f"\t{lFile} - {lDocPath}")

            lComps = _parsePythonFile(lFullPath)

            # CLASSE(S) Section
            if lComps["classes"]:
                lDetailLines.append("\t\tCLASSE(S):")
                for lCls in lComps["classes"]:
                    lDetailLines.append(f"\t\t\t{lCls} -> {lDocPath}: {lCls.lower()}")

            # FUNCTION(S) Section
            if lComps["functions"]:
                lDetailLines.append("\t\tFUNCTION(S):")
                for lFunc in lComps["functions"]:
                    lDetailLines.append(f"\t\t\t{lFunc} -> {lDocPath}: {lFunc.lower()}")

            # CONSTANTS(S)/GLOBAL(S) Section
            if lComps["constants"] or lComps["globals"]:
                lDetailLines.append("\t\tCONSTANTS(S)/GLOBAL(S)")
                for lConst in lComps["constants"]:
                    lDetailLines.append(
                        f"\t\t\t{lConst} -> {lDocPath}: {lConst.lower()}"
                    )
                for lGlob in lComps["globals"]:
                    lDetailLines.append(f"\t\t\t{lGlob} -> {lDocPath}: {lGlob.lower()}")

        lDetailLines.append("")

    return lDetailLines


def generateInventory():
    os.makedirs(C_DOCS_DIR, exist_ok=True)
    lCurrentTime = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    lLines = [
        "# eNuts Asset & Directory Inventory",
        f"*Auto-generated on: {lCurrentTime}*",
        "",
        "## Current Directory Structure",
        "",
        "```text",
        "eNuts/",
    ]

    lLines.extend(_buildTreeLines(C_TARGET_DIR))
    lLines.append("```")

    lLines.extend(["", "---", "", "## File Details & Code Components", "", "```text"])
    lLines.extend(_buildFileDetailsLines())
    lLines.append("```")

    lLines.extend(["", "---", "", "## Change Summary", "", "```text"])

    lHistory = _parseChangeHistory(C_MAX_COMMITS)
    if not lHistory:
        lLines.append("*No recent commit history found.*")
    else:
        for lEntry in lHistory:
            lLines.append(f"{lEntry['hash']}:")
            lLines.append(f"\t{lEntry['subject']}")
            for lFileInvolve in lEntry["files"]:
                lLines.append(f"\t\t{lFileInvolve}")
            lLines.append("")
    lLines.append("```")

    with open(C_OUTPUT_FILE, "w", encoding="utf-8") as lFileHandle:
        lFileHandle.write("\n".join(lLines))

    print(f"Successfully generated {C_OUTPUT_FILE}")


if __name__ == "__main__":
    generateInventory()
