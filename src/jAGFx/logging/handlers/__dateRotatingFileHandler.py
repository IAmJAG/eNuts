# ==================================================================================
import logging
import os

# ==================================================================================
from datetime import datetime

# ==================================================================================
import pytz


# ==================================================================================
class DateRotatingFileHandler(logging.FileHandler):
    KEY_ROOT: str = "LOGS"
    KEY_BACK: str = "BACKUP"
    KEY_ARCH: str = "ARCHIVE"
    def __init__(
        self,
        filenameTemplate,
        encoding=None,
        errors=None,
        dateFormat: str = "%Y%m%d",
        maximumBackups: int = 10,
        maximumLogs: int = 5,
        directories: list[str] = ["."],
        maximumSize: int = 10000000,  # 10 MB default size
        logExtension: str = "log",
        archiveTimeStampFormat: str = "%Y%m%d%H%M%S%",
        archiveRetention: int = 15,  # 15 days
        timezone: str | None = None,  # Add timezone parameter, None
    ):
        try:
            if not isinstance(directories, list):
                directories = list(directories)

            lDirs: dict = {
                self.KEY_ROOT: directories[0] if len(directories) > 0 else DateRotatingFileHandler.KEY_ROOT.lower(),
                self.KEY_BACK: directories[1] if len(directories) > 1 else DateRotatingFileHandler.KEY_BACK.lower(),
                self.KEY_ARCH: directories[2] if len(directories) > 2 else DateRotatingFileHandler.KEY_ARCH.lower(),
            }

            for key in list(lDirs.keys())[1:]:
                lDir: str = lDirs[key]
                if key != self.KEY_ROOT.lower():
                    lDir = os.path.join(lDirs[self.KEY_ROOT], lDirs[key])
                os.makedirs(lDir, exist_ok=True)                

            self._encoding = encoding
            self._errors = errors

            self._directories: dict[str, str] = lDirs
            self._maximumLogs: int = (
                1
                if maximumLogs is None
                or not isinstance(maximumLogs, int)
                or maximumLogs < 1
                else maximumLogs
            )
            self._maximumBackups: int = (
                1
                if maximumBackups is None
                or not isinstance(maximumBackups, int)
                or maximumBackups < 1
                else maximumBackups
            )
            self._maximumSize: int = (
                10000000
                if maximumSize is None
                or not isinstance(maximumSize, int)
                or maximumSize < 10000000
                else maximumSize
            )
            self._logfileExtention: str = logExtension
            self._archiveDateFormat: str = archiveTimeStampFormat
            self._archiveRetention: int = archiveRetention

            self._dateFormat: str = dateFormat
            self._filenameTemplate: str = filenameTemplate
            self._baseFilename: str = ""
            self._currentLogPath: str = ""

            self._fileSize: int = 0
            self._timezone = (
                pytz.timezone(timezone) if timezone else datetime.now().astimezone().tzinfo
            )
            self._stream = None
            self._xRotate()

            super().__init__(
                self._currentLogPath,
                mode="a",
                encoding=encoding,
                delay=False,
                errors=errors,
            )
        except Exception as ex:
            raise ex

    def _getTimeStampedFilename(self, template: str, ext: str = "log", datetimeFormat: str = "%Y%m%d"):
        now = datetime.now(self._timezone)  # Use timezone-aware datetime
        return f"{template.format(timestamp=now.strftime(datetimeFormat))}.{ext}"

    def _rotate(self):
        self.close()
        self._xRotate()
        self._open()

    def _xRotate(self):
        self._currentLogPath = os.path.join(
            self._directories[self.KEY_ROOT],
            self._getTimeStampedFilename(
                self._filenameTemplate, self._logfileExtention, self._dateFormat
            ),
        )
        self._baseFilename = os.path.splitext(self._currentLogPath)[0]

        self.baseFilename = self._currentLogPath        

        self._manageArchives()

    def _shiftBackup(self):
        lRootDir: str = self._directories[self.KEY_ROOT]
        lBackupDir: str = os.path.join(lRootDir, self._directories[self.KEY_BACK])

        lFromBackDir = [
            {"File": f, "Directory": lBackupDir}
            for f in os.listdir(lBackupDir)
            if f.startswith(self._baseFilename) and f.endswith(".bak")
        ]

        lBackupList = [
            {"File": f, "Directory": lBackupDir}
            for f in os.listdir(lRootDir)
            if f.startswith(self._baseFilename) and f.endswith(".bak")
        ]

        lBackupList.extend(lFromBackDir)
        lBackupList.sort(key=lambda item: item["File"], reverse=True)

        lSeq = len(lBackupList)
        while len(lBackupList) > 0:
            lBackupInfo = lBackupList.pop()
            lOldBackupPath = os.path.join(
                lBackupInfo["Directory"], lBackupInfo["File"]
            )

            lNewBackupPath = os.path.join(
                lBackupInfo["Directory"], f"{self._baseFilename}({lSeq:03}).bak"
            )
            os.rename(lOldBackupPath, lNewBackupPath)
            lSeq -= 1

    def _shouldRotate(self):
        lCurrFilePath = os.path.join(
            self._directories[self.KEY_ROOT],
            self._getTimeStampedFilename(self._filenameTemplate, self._logfileExtention, self._dateFormat),
        )

        lFilenameRotate = lCurrFilePath != self._currentLogPath
        lFileSizeRotate = self._fileSize >= self._maximumSize

        if lFilenameRotate or lFileSizeRotate:
            self._shiftBackup()
            os.rename(self._currentLogPath, f"{self._baseFilename}(000).bak")

        return lFilenameRotate or lFileSizeRotate

    def format(self, record):
        try:
            formatedMsg = super().format(record)
            self._fileSize += len(formatedMsg)

            return formatedMsg

        except ValueError:
            return ""

        except Exception as e:
            raise e

    def _manageArchives(self):
        self._archiveOldLogs()
        self._archiveOldBackups()
        self._purgeOldArchives()

    def _archiveOldLogs(self):
        lRootDir: str = self._directories[self.KEY_ROOT]
        lSortedLogFiles = sorted(
            [f for f in os.listdir(lRootDir) if f.startswith(self._baseFilename) and f.endswith(".log")],
            key=lambda f: os.path.getctime(os.path.join(lRootDir, f)),
            reverse=True,
        )

        try:
            lArchDir: str = os.path.join(lRootDir, self._directories[self.KEY_ARCH])
            while len(lSortedLogFiles) > self._maximumLogs:
                lOldLogFile = lSortedLogFiles.pop()
                lOldLogPath = os.path.join(lRootDir, lOldLogFile)
                lArchivePath = os.path.join(
                    lArchDir,
                    f"{lOldLogFile}.{datetime.now(self._timezone).strftime(self._archiveDateFormat)}",
                )
                os.rename(lOldLogPath, lArchivePath)

        except OSError as e:
            raise e

        except Exception as e:
            raise e

    def _archiveOldBackups(self):
        lRootDir: str
        try:
            lRootDir = self._directories[self.KEY_ROOT]
            lSortedBackups = sorted(
                [
                    f
                    for f in os.listdir(lRootDir)
                    if f.startswith(self._baseFilename + ".") and f.endswith(".bak")
                ],

                key=lambda f: os.path.getctime(
                    os.path.join(lRootDir, f)
                ),
                reverse=True,
            )

        except Exception as ex:
            raise ex

        lBackDir: str = os.path.join(lRootDir, self._directories[self.KEY_BACK])
        while len(lSortedBackups) > self._maximumBackups:
            lOldestBackup = lSortedBackups.pop()

            lOldBackupPath = os.path.join(lRootDir, lOldestBackup)
            lArchivePath = os.path.join(
                lBackDir,
                f"{lOldestBackup}.{datetime.now(self._timezone).strftime(self._archiveDateFormat)}",
            )

            try:
                os.rename(lOldBackupPath, lArchivePath)

            except OSError as e:
                logging.error(f"Error archiving backup: {e}")

            except Exception as e:
                raise e

    def _purgeOldArchives(self):
        lNow = datetime.now(self._timezone)  # Timezone-aware "now"
        lArchDir: str = os.path.join(self._directories[self.KEY_ROOT], self._directories[self.KEY_ARCH])
        lBackDir: str = os.path.join(self._directories[self.KEY_ROOT], self._directories[self.KEY_BACK])
        for lDirToArch in [lArchDir, lBackDir]:
            for lFilename in os.listdir(lDirToArch):
                lFilePath = os.path.join(lDirToArch, lFilename)
                if not os.path.isdir(lFilePath):
                    try:
                        # Attempt to extract the timestamp from the filename. Handles both .log.YYYYMMDDHHMMSS and .bak.YYYYMMDDHHMMSS
                        lFileParts = lFilename.split(".")
                        if len(lFileParts) >= 3:
                            lTimeStampStr = lFileParts[-1]
                            try:  # nested try to handle potential datetime parse errors
                                lArchiveTime = datetime.strptime(
                                    lTimeStampStr, self._archiveDateFormat
                                ).replace(
                                    tzinfo=self._timezone
                                )  # Make archive time timezone-aware
                                lTimeDiff = (
                                    lNow - lArchiveTime
                                )  # Compare timezone-aware datetimes
                                if lTimeDiff.days > self._archiveRetention:
                                    os.remove(lFilePath)

                            except ValueError:
                                logging.warning(
                                    f"Could not parse timestamp in filename: {lFilename}. Skipping deletion."
                                )

                        else:
                            logging.warning(
                                f"Could not parse timestamp in filename: {lFilename}. Skipping deletion."
                            )

                    except OSError as e:
                        raise e

                    except Exception as e:
                        raise e

    def close(self):
        self._fileSize = 0
        return super().close()

    def _open(self):
        self._fileSize = 0
        return open(
            self._currentLogPath, "a", encoding=self._encoding, errors=self._errors
        )

    def emit(self, record):
        try:
            if self._shouldRotate():
                self._rotate()

            super().emit(record)

        except ValueError:
            pass

        except Exception as e:
            raise e
