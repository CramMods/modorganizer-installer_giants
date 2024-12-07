from mobase import IPlugin

from .plugin import InstallerPlugin


def createPlugin() -> IPlugin:
    return InstallerPlugin()
