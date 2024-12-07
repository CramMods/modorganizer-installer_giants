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

    def xmlElement(self, xPath: str) -> et.Element:
        element = self._root.find(xPath)
        if element is None:
            raise Exception("Element not found")
        return element

    def xmlText(self, xPath: str) -> str:
        element = self.xmlElement(xPath)
        text = element.text
        if text is None:
            raise Exception("Element does not contain text")
        return text

    def xmlAttribute(self, xPath: str, attribute: str) -> str:
        element = self.xmlElement(xPath)
        if attribute not in element.attrib.keys():
            raise Exception("Element does not contain attribute")
        return element.attrib[attribute]


class ModManifest(Manifest):
    def name(self) -> str:
        return self.xmlText("./title/en")

    def author(self) -> str:
        return self.xmlText("./author")

    def version(self) -> str:
        return self.xmlText("./version")

    def description(self) -> str:
        return (
            self.xmlText("./description/en")
            .strip()
            .removeprefix("<![CDATA[")
            .removesuffix("]]>")
            .strip()
        )
