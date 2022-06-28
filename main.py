from recorder import Screenwindow
from recorder import Recorder
import PySimpleGUI as sg

version = 0.4


def main():
    screenViewer = Screenwindow(100)
    screenRecorder = Recorder()
    layout = [
        [sg.Button('Start', k='OffButton', size=(0, 3), expand_x=True)],
        [sg.Text('Time out:'), sg.Slider((20, 100), k='timeOut', size=(0, 2), orientation='h', expand_x=True), sg.Text('Sensitivity:'), sg.Slider((100, 2000), 200, k='area', size=(0, 2), orientation='h', expand_x=True)],
        [sg.Text('Person trigger:'), sg.Slider((50, 500), 150, k='person', size=(0, 2), orientation='h', expand_x=True)],
        [sg.Button('Enable Sound', k='snd', size=(0, 2), disabled=True, expand_x=True), sg.Button('Reset trigger', k='trigger', size=(0, 2), expand_x=True)],
        [sg.Image(filename='', key='image')]
    ]
    window = sg.Window('Tortops Vending', layout, size=(500, 800), resizable=True, keep_on_top=True)
    while True:
        event, values = window.read(timeout=round(1000 / 15))
        if event == 'OffButton':
            if screenViewer.is_running:
                screenViewer.stop(int(values['timeOut']) * 5)
                screenViewer = Screenwindow()
                window['OffButton'].update('Start')
                window['snd'].update(disabled=True)
            else:
                screenViewer.start()
                window['OffButton'].update('Running')
                window['snd'].update(disabled=False)
                screenViewer.switch_play_sound(True)
                window['snd'].update('Disable Sound')
        elif event == 'snd':
            if screenViewer.switch_play_sound():
                window['snd'].update('Disable Sound')
            else:
                window['snd'].update('Enable Sound')
        elif event == 'trigger':
            screenViewer.reset_trigger(int(values['timeOut']) * 5)
            window.ding()
            window['OffButton'].update('Running')
        elif event == sg.WIN_CLOSED or event == 'Exit':
            break
        if screenViewer.is_running:
            if screenViewer.triggered is True:
                if not screenRecorder.is_recording():
                    screenRecorder.start_recording('hola')
                window['OffButton'].update(f'Waiting {screenViewer.timeout / 5} seg')
                screenViewer.timeout -= 1
                if screenViewer.timeout <= 0:
                    window['OffButton'].update('Running')
                    screenViewer.triggered = False
                    screenViewer.timeout = int(values['timeOut']) * 5
                    window.ding()
            else:
                if screenRecorder.is_recording():
                    screenRecorder.stop_recording()
        x1, y1 = window.current_location()
        x2, y2 = window.current_location()
        x2_offset, y2_offset = window.current_size_accurate()
        x_offset = x2_offset
        y_offset = 200
        imgbytes = screenViewer.run_window(int(values['area']), (x1 - x_offset, y1 + y_offset, x2 + x2_offset - x_offset, y2 + y2_offset), int(values['person']))
        window['image'].update(data=imgbytes)
        window.set_title(f'V.{version} Triggered: {screenViewer.triggered}, Timeout: {screenViewer.timeout}, person (?: {screenViewer.is_person}')
    window.close()


if __name__ == "__main__":
    main()
