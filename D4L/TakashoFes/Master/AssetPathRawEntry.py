# automatically generated by the FlatBuffers compiler, do not modify

# namespace: Master

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class AssetPathRawEntry(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = AssetPathRawEntry()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsAssetPathRawEntry(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    @classmethod
    def AssetPathRawEntryBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x44\x34\x41\x4F", size_prefixed=size_prefixed)

    # AssetPathRawEntry
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # AssetPathRawEntry
    def Id(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int64Flags, o + self._tab.Pos)
        return 0

    # AssetPathRawEntry
    def AssetPath(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # AssetPathRawEntry
    def HashedPath(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # AssetPathRawEntry
    def FileHash(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # AssetPathRawEntry
    def FileSize(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # AssetPathRawEntry
    def FileRev(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # AssetPathRawEntry
    def FileType(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # AssetPathRawEntry
    def DownloadOption(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

def AssetPathRawEntryStart(builder): builder.StartObject(8)
def Start(builder):
    return AssetPathRawEntryStart(builder)
def AssetPathRawEntryAddId(builder, id): builder.PrependInt64Slot(0, id, 0)
def AddId(builder, id):
    return AssetPathRawEntryAddId(builder, id)
def AssetPathRawEntryAddAssetPath(builder, assetPath): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(assetPath), 0)
def AddAssetPath(builder, assetPath):
    return AssetPathRawEntryAddAssetPath(builder, assetPath)
def AssetPathRawEntryAddHashedPath(builder, hashedPath): builder.PrependUOffsetTRelativeSlot(2, flatbuffers.number_types.UOffsetTFlags.py_type(hashedPath), 0)
def AddHashedPath(builder, hashedPath):
    return AssetPathRawEntryAddHashedPath(builder, hashedPath)
def AssetPathRawEntryAddFileHash(builder, fileHash): builder.PrependUOffsetTRelativeSlot(3, flatbuffers.number_types.UOffsetTFlags.py_type(fileHash), 0)
def AddFileHash(builder, fileHash):
    return AssetPathRawEntryAddFileHash(builder, fileHash)
def AssetPathRawEntryAddFileSize(builder, fileSize): builder.PrependInt32Slot(4, fileSize, 0)
def AddFileSize(builder, fileSize):
    return AssetPathRawEntryAddFileSize(builder, fileSize)
def AssetPathRawEntryAddFileRev(builder, fileRev): builder.PrependInt32Slot(5, fileRev, 0)
def AddFileRev(builder, fileRev):
    return AssetPathRawEntryAddFileRev(builder, fileRev)
def AssetPathRawEntryAddFileType(builder, fileType): builder.PrependInt32Slot(6, fileType, 0)
def AddFileType(builder, fileType):
    return AssetPathRawEntryAddFileType(builder, fileType)
def AssetPathRawEntryAddDownloadOption(builder, downloadOption): builder.PrependInt32Slot(7, downloadOption, 0)
def AddDownloadOption(builder, downloadOption):
    return AssetPathRawEntryAddDownloadOption(builder, downloadOption)
def AssetPathRawEntryEnd(builder): return builder.EndObject()
def End(builder):
    return AssetPathRawEntryEnd(builder)