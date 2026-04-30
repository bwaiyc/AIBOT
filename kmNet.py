"""Fallback kmNet module for non-native environments."""


def init(ip, port, uuid):
    return True


def move(dx, dy):
    return True


def left(down):
    return True


def monitor(value):
    return True


def unmask_all():
    return True


def isdown_left():
    return False


def isdown_right():
    return False


def isdown_middle():
    return False


def isdown_side1():
    return False


def isdown_side2():
    return False


def mask_left(v):
    return True


def mask_right(v):
    return True


def mask_middle(v):
    return True


def mask_side1(v):
    return True


def mask_side2(v):
    return True


def mask_x(v):
    return True


def mask_y(v):
    return True


def mask_wheel(v):
    return True

