"""Fallback Makcu controller.

This shim keeps the application importable when the real Makcu SDK
is not present in the current environment.
"""


class MakcuController:
    def __init__(self):
        self.button_states = {0: False, 1: False, 2: False, 3: False, 4: False}
        self._connected = True

    def connect(self):
        self._connected = True
        return True

    def disconnect(self):
        self._connected = False
        return True

    def move(self, dx, dy):
        return bool(self._connected)

    def left(self, down):
        self.button_states[0] = bool(down)
        return True

    def lock_ml(self, value):
        return True

    def lock_mr(self, value):
        return True

    def lock_mm(self, value):
        return True

    def lock_ms1(self, value):
        return True

    def lock_ms2(self, value):
        return True

    def lock_mx(self, value):
        return True

    def lock_my(self, value):
        return True

