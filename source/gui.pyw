import flet as ft
from flet_core.control_event import ControlEvent
from flet_core import theme
import main as mn
from time import sleep
import pythoncom
import darkdetect
import ctypes
import sys

'''
# Use this part of code if you want to request UAC elevation
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(0)
'''
valorant_path = mn.set_saved_config_path()


def main(page: ft.Page):
    page.title = "VALORez"
    page.padding = 0
    page.window_opacity = 0.98
    page.theme = theme.Theme(color_scheme_seed="red500")

    page.theme_mode = ft.ThemeMode.SYSTEM
    if darkdetect.isDark():
        page.bgcolor = "#1A1C1E"

    page.snack_bar = ft.SnackBar(
        content=ft.Text(mn.output_var),
        duration=1000,
    )

    page.fonts = {
        "VALORANT": r"fonts/ValorantFont.ttf",
    }

    page.window_width = 400
    page.window_height = 500

    page.window_resizable = False
    page.window_maximizable = False
    page.window_minimizable = False

    page.window_center()
    page.window_to_front()

    page.update()

    # ===================================================

    def closing(e: ControlEvent):
        page.window_destroy()

    def startvalorant(e: ControlEvent):
        pythoncom.CoInitialize()
        mn.parse()
        animate_opacityp()
        mn.execute_valorant(valorant_path)
        animate_opacityp()
        page.snack_bar = ft.SnackBar(content=ft.Text(mn.output_var), duration=1000)
        page.snack_bar.open = True
        page.update()

    def defaultres(e: ControlEvent):
        mn.set_resolution_default()
        dd.value = 0
        sleep(0.25)
        page.snack_bar = ft.SnackBar(content=ft.Text(mn.output_var), duration=1000)
        page.snack_bar.open = True
        page.update()

    def cleardropdown(e: ControlEvent):
        dd.value = 0
        mn.output_var = 'Input cleared.'
        page.snack_bar = ft.SnackBar(content=ft.Text(mn.output_var), duration=1000)
        page.snack_bar.open = True
        mn.write_saved_config_res('0', '0')
        page.update()

    def confirmres(e: ControlEvent):
        animate_opacityp()
        try:
            if dd.value != 0 and dd.value is not None:
                mn.execute_stretch()
            width = ''
            height = ''
            i = 0
            for char in dd.value:
                if char != ' ':
                    i += 1
                    width += char
                else:
                    break
            try:
                for char in dd.value[i + 3:]:
                    height += char
            except:
                pass
            mn.write_saved_config_res(width, height)
            mn.set_resolution(int(width), int(height))
            mn.output_var = "VALORANT is now stretched!"
        except:
            mn.output_var = "VALORANT isn't started!"
        if dd.value == 0 or dd.value is None:
            mn.output_var = "Please select your resolution."
        dd.value = 0
        animate_opacityp()
        page.snack_bar = ft.SnackBar(content=ft.Text(mn.output_var), duration=1000)
        page.snack_bar.open = True
        page.update()

    def animate_opacityc():
        c.opacity = 1 if c.opacity == 0 else 0
        c.update()

    def animate_opacityp():
        processbar.opacity = 1 if processbar.opacity == 0 else 0
        processbar.update()

    title = ft.Text(
        "VALORez",
        color="red700",
        size=46,
        font_family='VALORANT',
        text_align=ft.TextAlign.CENTER,
        width=page.window_width,
    )

    dd = ft.Dropdown(
        width=175,
        suffix_icon=ft.icons.SCREENSHOT_MONITOR,
        content_padding=7,
        border_radius=20,
        focused_border_color='white',
        hint_text=" ____ x ____",
        options=[
        ],
    )

    confirm = ft.IconButton(
        icon=ft.icons.CHECK,
        icon_color='green',
        on_click=confirmres,
    )

    default = ft.IconButton(
        icon=ft.icons.RESET_TV,
        on_click=defaultres,
    )

    clear = ft.IconButton(
        icon=ft.icons.DELETE,
        on_click=cleardropdown,
    )

    def on_dialog_result(e: ft.FilePickerResultEvent):
        global valorant_path
        try:
            valorant_path = e.files[0].path
            print(valorant_path)
        except:
            pass

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    page.update()

    folder_button = ft.IconButton(
        icon=ft.icons.FOLDER,
        on_click=lambda _: file_picker.pick_files(allowed_extensions=["exe"],
                                                  dialog_title="Open RiotClientServices.exe", allow_multiple=False),
    )

    start = ft.ElevatedButton(
        content=ft.Container(
            content=ft.Text(
                "Patch & Start VALORANT",
                weight=ft.FontWeight.BOLD,
            ),
        ),
        height=40,
        width=page.window_width - 127,
        on_click=startvalorant,
        style=ft.ButtonStyle(
            animation_duration=500,
            overlay_color='transparent',
            bgcolor={ft.MaterialState.DEFAULT: page.bgcolor, ft.MaterialState.PRESSED: 'red300'},
            shape={
                ft.MaterialState.HOVERED: ft.RoundedRectangleBorder(radius=90),
                ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=5),
            },
        ),
    )

    close = ft.ElevatedButton(
        content=ft.Container(
            content=ft.Text(
                "Close",
                weight=ft.FontWeight.BOLD,
            ),
        ),
        height=40,
        width=page.window_width - 75,
        on_click=closing,
        style=ft.ButtonStyle(
            animation_duration=500,
            overlay_color='transparent',
            bgcolor={ft.MaterialState.DEFAULT: page.bgcolor, ft.MaterialState.PRESSED: 'red300'},
            shape={
                ft.MaterialState.HOVERED: ft.RoundedRectangleBorder(radius=90),
                ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=5),
            },
        ),
    )

    r_firstline = ft.Row(
        [
            start,
            folder_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    r_resolution = ft.Row(
        [
            dd,
            confirm,
            default,
            clear,
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    r_close = ft.Row(
        [
            close
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    contitle = ft.Container(
        content=title,
        padding=ft.padding.only(top=30),
    )

    con = ft.Container(
        content=r_firstline,
        padding=15
    )

    conclose = ft.Container(
        content=r_close,
        padding=ft.padding.only(top=15, bottom=100),
    )

    processbar = ft.Container(
        content=ft.ProgressBar(
            width=400,
            color="red700",
            bgcolor=page.bgcolor,
        ),
        width=page.window_width,
        animate_opacity=100,
    )

    c = ft.Container(
        content=ft.Column(
            [
                contitle,
                con,
                r_resolution,
                conclose,
                ft.Text(f"           NEM3S", size=10, opacity=0.5)
            ]
        ),
        height=447,
        animate_opacity=0,
    )

    page.add(c, processbar)

    mn.create_saved_config()
    confirm.disabled = True
    close.disabled = True
    default.disabled = True
    clear.disabled = True
    start.disabled = True
    animate_opacityc()
    c.animate_opacity = 250
    sleep(1.2)
    confirm.disabled = False
    close.disabled = False
    default.disabled = False
    clear.disabled = False
    start.disabled = False
    listsorted = mn.get_all_resolutions()
    listsorted.sort(reverse=True)
    for i in range(len(listsorted)):
        dd.options.append(ft.dropdown.Option('{} x {}'.format(listsorted[i][0], listsorted[i][1])))
        page.update()
    animate_opacityp()
    animate_opacityc()
    mn.set_saved_config_res(dd)
    page.update()


if __name__ == '__main__':
    ft.app(target=main, assets_dir="assets")
