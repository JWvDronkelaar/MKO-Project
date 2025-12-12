import sys
import os

if os.name == "nt":
    import msvcrt
else:
    import select
    import tty
    import termios


class Keyboard:
    """
    Cross-platform non-blocking keyboard polling.
    Supports detecting ESC from terminal without blocking.
    """

    def __init__(self):
        self._orig_settings = None

        if os.name != "nt":
            self._orig_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())

    def read_key(self):
        """
        Returns an int representing the key pressed, or None.
        ESC is returned as 27.
        """
        if os.name == "nt":
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                return ch[0]
            return None

        # POSIX
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return ord(sys.stdin.read(1))
        return None

    def restore(self):
        if os.name != "nt" and self._orig_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._orig_settings)
