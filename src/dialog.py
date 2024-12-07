from PyQt6.QtWidgets import QDialog, QWidget

from mobase import GuessedString

from .common.manifest import ModManifest
from .ui.installerdialog import Ui_InstallerDialog


class InstallerDialog(QDialog):
    _manual: bool
    _ui: Ui_InstallerDialog

    def __init__(
        self, parent: QWidget, name: GuessedString, manifest: ModManifest
    ) -> None:
        super().__init__(parent)
        self._manual = False

        # Setup UI
        self._ui = Ui_InstallerDialog()
        self._ui.setupUi(self)  # pyright: ignore[reportUnknownMemberType]

        # Fill UI text
        self._ui.NameValue.addItems(name.variants())
        self._ui.NameValue.setCurrentIndex(self._ui.NameValue.findText(str(name)))
        self._ui.AuthorValue.setText(manifest.author())
        self._ui.VersionValue.setText(manifest.version())
        self._ui.DescriptionValue.setText(manifest.description())

        # Connect UI buttons
        self._ui.CancelButton.clicked.connect(self.reject)  # pyright: ignore[reportUnknownMemberType]
        self._ui.ManualButton.clicked.connect(self._manualClicked)  # pyright: ignore[reportUnknownMemberType]
        self._ui.InstallButton.clicked.connect(self.accept)  # pyright: ignore[reportUnknownMemberType]

    def _manualClicked(self) -> None:
        self._manual = True
        self.reject()

    def manual(self) -> bool:
        return self._manual

    def name(self) -> str:
        return self._ui.NameValue.currentText()
