import os
import ctypes
from ctypes import wintypes
import threading

class HotkeyManager:
    """
    Global hotkey manager using RegisterHotKey (WinAPI) for maximum reliability in Windows 
    without triggering excessive antivirus alerts compared to hooking libraries.
    """
    def __init__(self, callback_next, callback_prev):
        self.callback_next = callback_next
        self.callback_prev = callback_prev
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._msg_loop, daemon=True)
        self.thread.start()

    def _msg_loop(self):
        # RegisterHotKey(hWnd, id, fsModifiers, vk)
        # MOD_WIN = 0x0008, MOD_SHIFT = 0x0004
        # VK_F5 = 0x74
        user32 = ctypes.windll.user32
        
        # ID 1: Win + F5
        if not user32.RegisterHotKey(None, 1, 0x0008, 0x74):
            print("Failed to register Win+F5")
            
        # ID 2: Win + Shift + F5
        if not user32.RegisterHotKey(None, 2, 0x0008 | 0x0004, 0x74):
            print("Failed to register Win+Shift+F5")

        try:
            msg = ctypes.wintypes.MSG()
            while self.running and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312: # WM_HOTKEY
                    if msg.wParam == 1:
                        self.callback_next()
                    elif msg.wParam == 2:
                        self.callback_prev()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)
            user32.UnregisterHotKey(None, 2)

    def stop(self):
        self.running = False
        # To break the GetMessageW loop, we could post a dummy message
        if os.name == 'nt':
            ctypes.windll.user32.PostQuitMessage(0)
