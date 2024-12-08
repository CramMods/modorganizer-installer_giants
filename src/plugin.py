import re
from pathlib import Path
from typing import Union, cast

from PyQt6.QtWidgets import QDialog

from mobase import (
    FileTreeEntry,
    GuessedString,
    GuessQuality,
    IFileTree,
    IModInterface,
    InstallResult,
    IOrganizer,
    IPluginInstallerSimple,
    PluginSetting,
    VersionInfo,
)

from .common.manifest import ModManifest
from .dialog import InstallerDialog


class InstallerPlugin(IPluginInstallerSimple):
    _organizer: IOrganizer
    _installingArchive: str
    _supportedGames: list[str] = ["farmingsimulator25"]

    # IPlugin Implementation

    def name(self) -> str:
        return "GIANTS Mod Installer"

    def author(self) -> str:
        return "Cram42"

    def version(self) -> VersionInfo:
        return VersionInfo("1.1.0")

    def description(self) -> str:
        return "Installer for GIANTS Software game mods"

    def settings(self) -> list[PluginSetting]:
        return [PluginSetting("priority", "priority of this installer", 120)]

    def init(self, organizer: IOrganizer) -> bool:
        self._organizer = organizer
        return True

    # IPluginInstaller Implementation

    def isArchiveSupported(self, tree: IFileTree) -> bool:
        currentGame = self._organizer.managedGame().gameShortName()
        supportedGame = currentGame in self._supportedGames
        hasManifest = tree.exists("modDesc.xml", FileTreeEntry.FileTypes.FILE)
        return supportedGame & hasManifest

    def isManualInstaller(self) -> bool:
        return False

    def priority(self) -> int:
        return cast(int, self._organizer.pluginSetting(self.name(), "priority"))

    def onInstallationStart(
        self, archive: str, reinstallation: bool, current_mod: IModInterface
    ) -> None:
        self._installingArchive = archive
        return super().onInstallationStart(archive, reinstallation, current_mod)

    # IPluginInstallerSimple Implementation

    def install(
        self, name: GuessedString, tree: IFileTree, version: str, nexus_id: int
    ) -> Union[InstallResult, IFileTree, tuple[InstallResult, IFileTree, str, int]]:
        # Get manifest
        manifestFile = tree.find("modDesc.xml", FileTreeEntry.FileTypes.FILE)
        if not isinstance(manifestFile, FileTreeEntry):
            raise Exception("manifest not found")
        manifestPath = self._manager().extractFile(manifestFile)
        manifest = ModManifest(manifestPath)

        # Update name from manifest
        name.update(manifest.name(), GuessQuality.GOOD)

        # Create new tree with inside folder with archive name
        newTree = tree.createOrphanTree()
        folderName = Path(self._installingArchive).stem
        folderName = re.sub(r"\W+", "", folderName)
        newTree.addDirectory(folderName)
        for entry in tree:
            newTree.copy(entry, folderName + "/")

        # Present dialog
        dialog = InstallerDialog(self._parentWidget(), name, manifest)
        result = dialog.exec()

        # Update name from dialog
        name.update(dialog.name(), GuessQuality.USER)

        # Return result

        if result == QDialog.DialogCode.Accepted:
            return (InstallResult.SUCCESS, newTree, manifest.version(), 0)
        else:
            if dialog.manual():
                return (InstallResult.MANUAL_REQUESTED, newTree, manifest.version(), 0)
            else:
                return InstallResult.CANCELED
