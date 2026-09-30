# ==================================================================================
import os

# ==================================================================================
from json import dump, load

# ==================================================================================
from jAGFx.configuration import ApplicationConfiguration

# ==================================================================================
ASSETSDIR: str = "assets"
CONFIGDIR: str = "config"
FONTDIR: str = "fonts"
STYLEDIR: str = "styles"
ICONDIR: str = "icons"
# ==================================================================================

# ==================================================================================
def getAssetPath(assetDirectory: str):
    lDir: str = os.path.join(os.getcwd(), ASSETSDIR)
    return os.path.join(lDir, assetDirectory)

# ==================================================================================
def getStylePath(styleFileName: str = ""):
    lPath: str = STYLEDIR if styleFileName.strip() == "" else os.path.join(STYLEDIR, styleFileName)
    return os.path.join(ASSETSDIR, lPath)

# ==================================================================================
def getFontPath(fontFilename: str = ""):
    lPath: str = FONTDIR if fontFilename.strip() == "" else os.path.join(FONTDIR, fontFilename)
    return os.path.join(os.getcwd(), ASSETSDIR, lPath)

# ==================================================================================
def getICONPath(iconFilename: str = ""):
    lPath: str = ICONDIR if iconFilename.strip() == "" else os.path.join(ICONDIR, iconFilename)
    return os.path.join(os.getcwd(), ASSETSDIR, lPath)

# ==================================================================================
def getConfigPath(relativePath: str):
    lDir: str = os.path.join(os.getcwd(), CONFIGDIR)
    return os.path.join(lDir, relativePath)

# ==================================================================================
def getStyleSheet(filePath: str) -> str:
    """Function to read the QSS file and return it as a string."""
    if os.path.exists(filePath):
        with open(filePath, "r") as f:
            return f.read()
    else:
        raise FileNotFoundError(f"File {filePath} not found")

# ==================================================================================
def LoadCFG(path: str = getConfigPath("appconfig.json")) -> ApplicationConfiguration:
    with open(path) as file:
        jsonData = load(fp=file)
        cfg: ApplicationConfiguration = ApplicationConfiguration()
        cfg.decode(jsonData)
    return cfg

# ==================================================================================
def SaveCFG(path: str = getConfigPath("appconfig.json")):
    cfg: ApplicationConfiguration = Provider.Resolve(iConfiguration)  # type: ignore
    with open(path, "w") as file:
        cfg = dump(cfg.encode(), fp=file)
