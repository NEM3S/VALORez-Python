import os
from contextlib import suppress
from time import sleep
import win32process
import win32api
import win32con
import win32gui
import win32com.client
import pywintypes
import psutil
import ctypes
import configparser
import datetime
import pythoncom
import wmi

output_var = ''  # Information text for the GUI


# https://stackoverflow.com/questions/2398746/removing-window-border
def setup_window_border() -> None:
    """Disable borders (frame) of window and maximize window"""
    sleep(0.15)  # Delay before starting
    hwnd = win32gui.GetForegroundWindow()  # Get the handle of the focused window
    style = win32api.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~win32con.WS_MINIMIZEBOX
    style &= ~win32con.WS_MAXIMIZEBOX
    style &= ~win32con.WS_SYSMENU
    style &= ~win32con.WS_CAPTION
    style &= ~win32con.WS_SIZEBOX
    win32api.SetWindowLong(hwnd, win32con.GWL_STYLE, style)  # Set style to the window (disable borders)
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)  # Maximize the window


# https://stackoverflow.com/questions/70618975/python-get-windowtitle-from-process-id-or-process-name
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible


class SetWindowFocus:
    """Set a specified window in the foreground"""

    def __init__(self, processname) -> None:
        self.proc_name = processname

    def getProcessIDByName(self) -> list:
        pids_list = []
        process_name = self.proc_name

        for proc in psutil.process_iter():
            if process_name in proc.name():
                pids_list.append(proc.pid)

        return pids_list

    @staticmethod
    def get_hwnds_for_pid(pid) -> list:
        def callback(hwnd, hwnds) -> bool:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)

            if found_pid == pid:
                hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds

    def getWindowHandle(self) -> int:
        pids = self.getProcessIDByName()
        for i in pids:
            hwnds = self.get_hwnds_for_pid(i)
            for hwnd in hwnds:
                if IsWindowVisible(hwnd):
                    print(type(hwnd))
                    return hwnd

    def set_foreground(self) -> None:
        """Put the window in the foreground"""
        win32gui.SetForegroundWindow(self.getWindowHandle())


# https://github.com/k0nze/windows_resolution_switcher/blob/main/resolution_switcher.py
def set_resolution(width: int, height: int, refresh_rate: int = None) -> None:
    """Set a specified and existing resolution (and refresh rate)"""
    assert width <= max(get_all_resolutions())[0] and height <= max(get_all_resolutions())[1] and (
        width, height) in get_all_resolutions()
    try:
        display_option = pywintypes.DEVMODEType()
        display_option.PelsWidth = width  # Change the width
        display_option.PelsHeight = height  # Change the height
        display_option.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT  # Apply changes
        if width != max(get_all_resolutions())[0] and height != max(get_all_resolutions())[1]:
            display_option.DisplayFixedOutput = win32con.DMDFO_STRETCH  # Change the display scaling to stretched
            display_option.Fields |= win32con.DM_DISPLAYFIXEDOUTPUT  # Apply scaling change
        if refresh_rate:
            display_option.DisplayFrequency = refresh_rate  # Change the reflesh rate
            display_option.Fields |= win32con.DM_DISPLAYFREQUENCY  # Apply reflesh change
        win32api.ChangeDisplaySettings(display_option, win32con.CDS_UPDATEREGISTRY)  # Set changes
    except:
        pass


def set_resolution_default() -> None:
    """Set the resolution to the computer's highest resolution"""
    global output_var
    if win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS).PelsWidth == max(get_all_resolutions())[  # Check if the resolution is already set to default
        0] and win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS).PelsHeight == \
            max(get_all_resolutions())[1]:
        output_var = 'Resolution is already set to default.'
    else:
        display_option = pywintypes.DEVMODEType()
        display_option.PelsWidth = max(get_all_resolutions())[0]  # Change the width
        display_option.PelsHeight = max(get_all_resolutions())[1]  # Change the height
        display_option.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT  # Apply changes
        win32api.ChangeDisplaySettings(display_option, win32con.CDS_UPDATEREGISTRY)  # Set changes
        output_var = 'Resolution set to default.'


def get_all_resolutions() -> list:
    """Return every existing resolution of the computer, without duplication"""
    i = 0
    resolutions = []
    seen = set()
    max_width = 0
    max_height = 0
    with suppress(Exception):
        while True:
            ds = win32api.EnumDisplaySettings(None, i)
            res = (ds.PelsWidth, ds.PelsHeight)
            if res not in seen:
                seen.add(res)
                if ds.PelsWidth > max_width:
                    max_width = ds.PelsWidth
                if ds.PelsHeight > max_height:
                    max_height = ds.PelsHeight
                resolutions.append((ds.PelsWidth, ds.PelsHeight))
            i += 1
    return resolutions


def game_is_opened() -> bool:
    """Check if the game is opened"""
    if len(SetWindowFocus("VALORANT").getProcessIDByName()) != 0:
        return True
    else:
        return False


def execute_valorant() -> str:
    """Start the game"""
    global output_var
    found = []
    if game_is_opened():
        output_var = "VALORANT is already opened."
        return "The game is already opened."
    else:  # Check installation directory of Riot Client
        for drive in wmi.WMI().Win32_LogicalDisk():
            for path, dirs, files in os.walk("{}/Riot Games/".format(drive.Caption)):
                for name in files:
                    if "RiotClientServices.exe" in name:
                        found.append(path + "\\RiotClientServices.exe")
                        break
        if len(found) != 0:
            os.spawnl(os.P_NOWAIT, found[0], found[0], "--launch-product=valorant --launch-patchline=live")
            output_var = "Done!"
            return "Done!"
        else:
            output_var = "VALORANT or Riot Client may be not installed."
            return "The game or Riot Client may be not installed."


def execute_stretch() -> None:
    """Stretch the game when it's opened"""
    assert game_is_opened()
    win32com.client.Dispatch("WScript.Shell", pythoncom.CoInitialize()).SendKeys('%')
    SetWindowFocus("VALORANT").set_foreground()
    setup_window_border()


def found_file_bydate():
    """Find the lastest game config file"""
    p = os.path.expandvars(r"%LOCALAPPDATA%\VALORANT\Saved\Config")

    mylist = os.listdir(p)
    mylistfound = []

    for file in mylist:
        try:
            if file[8] == '-' and file[13] == '-' and file[18] == '-' and file[23] == '-':
                mylistfound.append(file)
        except:
            pass

    if len(mylistfound) != 0:
        maxfile = mylistfound[0]
        maxdate = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.expandvars(
            r"{}\{}\Windows\GameUserSettings.ini".format(p, maxfile))))

        for file in mylistfound:
            if datetime.datetime.fromtimestamp(
                    os.path.getmtime(
                        os.path.expandvars(r"{}\{}\Windows\GameUserSettings.ini".format(p, file)))) > maxdate:
                maxfile = file
        return maxfile
    else:
        return


def parse():
    """Set patch to game config"""
    global output_var
    config = configparser.ConfigParser()
    try:
        config.read(
            r"{}\{}\Windows\GameUserSettings.ini".format(os.path.expandvars(r"%LOCALAPPDATA%\VALORANT\Saved\Config"),
                                                         found_file_bydate()))
    except:
        output_var = "VALORANT isn't installed"
        return
    try:  # Add or change value of the "fullscreen" value
        if config[r'/Script/ShooterGame.ShooterGameUserSettings']['fullscreenmode'] != str(2):
            config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'fullscreenmode'.lower(), '2')
            with open(r"{}\{}\Windows\GameUserSettings.ini".format(
                    os.path.expandvars(r"%LOCALAPPDATA%\VALORANT\Saved\Config"), found_file_bydate()),
                    'w') as configfile:
                config.write(configfile)
    except:
        with open(r"{}\{}\Windows\GameUserSettings.ini".format(
                os.path.expandvars(r"%LOCALAPPDATA%\VALORANT\Saved\Config"), found_file_bydate()), 'r') as configfile:
            data = configfile.readlines()
        for index in range(len(data) - 1):
            if data[index] == '\n':
                data[index] = 'fullscreenmode = 2\n'
                break

        with open(r"{}\{}\Windows\GameUserSettings.ini".format(
                os.path.expandvars(r"%LOCALAPPDATA%\VALORANT\Saved\Config"), found_file_bydate()), 'w') as configfile:
            configfile.writelines(data)

    # Change values of other settings
    config.read(
        r"{}\{}\Windows\GameUserSettings.ini".format(os.path.expandvars(r"%LOCALAPPDATA%\VALORANT\Saved\Config"),
                                                     found_file_bydate()))

    config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'bshouldletterbox', 'False')
    config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'blastconfirmedshouldletterbox', 'False')
    config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'resolutionsizex',
               str(win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS).PelsWidth))
    config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'lastuserconfirmedresolutionsizex',
               str(win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS).PelsWidth))
    config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'resolutionsizey',
               str(win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS).PelsHeight - 30))
    config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'lastuserconfirmedresolutionsizey',
               str(win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS).PelsHeight - 30))
    config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'windowposy', '15')
    config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'lastconfirmedfullscreenmode', '2')
    config.set(r'/Script/ShooterGame.ShooterGameUserSettings', 'preferredfullscreenmode', '2')

    with open(r"{}\{}\Windows\GameUserSettings.ini".format(
            os.path.expandvars(r"%LOCALAPPDATA%\VALORANT\Saved\Config"), found_file_bydate()), 'w') as configfile:
        config.write(configfile)


def set_saved_config(widget) -> None:
    """Set saved resolution values from settings.ini"""
    config = configparser.ConfigParser()
    config.read(r"assets\config\settings.ini")
    resw = config['res']['resolutionw']
    resh = config['res']['resolutionh']
    if resw == '0' and resh == '0':
        return None
    else:
        widget.value = f"{resw} x {resh}"


def write_saved_config(width, height) -> None:
    """Overwrite resoltion values in the settings.ini"""
    config = configparser.ConfigParser()
    config.read(r"assets\config\settings.ini")
    config.set('res', 'resolutionw', width)
    config.set('res', 'resolutionh', height)
    with open(r"assets\config\settings.ini", 'w') as configfile:
        config.write(configfile)

