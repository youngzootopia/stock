import win32gui
import win32con
import win32api
import time
import json

# 클래스로 비밀번호 입력 만들어 놨으나, 스레드 분리 필요할 듯. 슬롯대기 스레드와 동시 작동 안함
class Login:
    def __init__(self):
        with open('./config/pass.json') as f:
            self.config = json.load(f)
        self.login()

    def window_enumeration_handler(self, hwnd, top_windows):
        top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


    def enum_windows(self):
        windows = []
        win32gui.EnumWindows(self.window_enumeration_handler, windows)
        return windows


    def find_window(self, caption):
        hwnd = win32gui.FindWindow(None, caption)
        if hwnd == 0:
            windows = self.enum_windows()
            for handle, title in windows:
                if caption in title:
                    hwnd = handle
                    break
        return hwnd


    def enter_keys(self, hwnd, data):
        win32api.SendMessage(hwnd, win32con.EM_SETSEL, 0, -1)
        win32api.SendMessage(hwnd, win32con.EM_REPLACESEL, 0, data)
        win32api.Sleep(300)


    def click_button(self, btn_hwnd):
        win32api.PostMessage(btn_hwnd, win32con.WM_LBUTTONDOWN, 0, 0)
        win32api.Sleep(100)
        win32api.PostMessage(btn_hwnd, win32con.WM_LBUTTONUP, 0, 0)
        win32api.Sleep(300)


    def login(self):
        caption = "Open API Login"
        hwnd = self.find_window(caption)

        #edit_id = win32gui.GetDlgItem(hwnd, 0x3E8)
        edit_pass = win32gui.GetDlgItem(hwnd, 0x3E9)
        #edit_cert = win32gui.GetDlgItem(hwnd, 0x3EA)
        btn_login = win32gui.GetDlgItem(hwnd, 0x1)

        #enter_keys(edit_id, "아이디")
        self.enter_keys(edit_pass, self.config['DEFAULT']['KIWOOM_PASS'])
        #enter_keys(edit_cert, "인증비밀번호")
        self.click_button(btn_login)
