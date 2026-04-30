"""Fallback i_KM implementation.

Provides a no-hardware stub so the app can run without the physical device.
"""


class i_KM:
    def __init__(self):
        self._open = False
        self._notify = 0

    def OpenDevice(self, com_port):
        self._open = True
        return True

    def IsOpen(self):
        return self._open

    def Close(self):
        self._open = False
        return True

    def GetModel(self):
        return 1

    def GetVersion(self):
        return "stub-1.0"

    def GetChipID(self):
        return "stub-chip-id"

    def GetStorageSize(self):
        return 0

    def SetWaitRespon(self, enabled):
        return True

    def Notify_Mouse(self, value):
        self._notify = int(value)
        return True

    def Read_Notify(self, timeout_ms):
        return b""

    def MoveR(self, dx, dy):
        return bool(self._open)

    def LeftDown(self):
        return True

    def LeftUp(self):
        return True

    def Lock_Mouse(self, value):
        return True

