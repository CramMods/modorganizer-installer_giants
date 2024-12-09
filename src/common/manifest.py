from __future__ import annotations

import xml.etree.cElementTree as et
from pathlib import Path


class Manifest:
    _path: str
    _root: et.Element

    def __init__(self, path: str) -> None:
        self._path = path

        xmlTree = et.parse(path)
        xmlRoot = xmlTree.getroot()
        if not isinstance(xmlRoot, et.Element):
            raise Exception("xml root not found")
        self._root = xmlRoot

    def path(self) -> str:
        return self._path

    def xmlRoot(self) -> et.Element:
        return self._root

    def xmlElement(self, xPath: str) -> et.Element | None:
        return self._root.find(xPath)

    def xmlText(self, xPath: str) -> str | None:
        element = self.xmlElement(xPath)
        return element.text if element is not None else None

    def xmlAttribute(self, xPath: str, attr: str) -> str | None:
        element = self.xmlElement(xPath)
        return (
            element.attrib[attr]
            if element is not None and attr in element.attrib.keys()
            else None
        )


class ModManifest(Manifest):
    def name(self) -> str:
        return self.xmlText("./title/en") or "UNKNOWN"

    def author(self) -> str:
        return self.xmlText("./author") or "UNKNOWN"

    def version(self) -> str:
        return self.xmlText("./version") or "UNKNOWN"

    def description(self) -> str:
        text = self.xmlText("./description/en") or ""
        return text.strip().removeprefix("<![CDATA[").removesuffix("]]>").strip()

    def storeItemManifestPaths(self) -> list[str]:
        paths: list[str] = []

        storeItems = self.xmlElement("./storeItems")
        if storeItems:
            for itemElement in storeItems.findall("storeItem"):
                relPath = itemElement.attrib["xmlFilename"]
                absPath = Path(self.path()).parent.joinpath(relPath).absolute()
                paths.append(str(absPath))

        return paths

    def storeItemManifests(self) -> list[StoreItemManifest]:
        return [StoreItemManifest(p) for p in self.storeItemManifestPaths()]

    def categories(self) -> list[str]:
        categories: list[str] = []
        for manifest in self.storeItemManifests():
            for category in manifest.categories():
                if category not in categories:
                    categories.append(category)
        return categories


class StoreItemManifest(Manifest):
    def type(self) -> str:
        return self.xmlRoot().tag

    def name(self) -> str:
        return self.xmlText("./storeData/name/en") or "UNKNOWN"

    def categories(self) -> list[str]:
        categories: list[str] = []

        text = self.xmlText("./storeData/category")
        if text is not None:
            textChunks = text.split(" ")
            for textChunk in textChunks:
                categories.append("store:{}".format(textChunk.strip()))

        return categories
