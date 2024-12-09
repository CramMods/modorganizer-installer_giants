import xml.etree.cElementTree as et


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

