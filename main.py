from recorder import Screenwindow
from recorder import Recorder
import PySimpleGUI as sg

version = 0.5


def main():
    TIMEOUT = 20
    screenViewer = Screenwindow(TIMEOUT)
    screenRecorder = Recorder()
    audios = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
    layout = [
        [sg.Button('Start', k='startBtn', size=(0, 3), expand_x=True)],
        [sg.Text('Time out:'), sg.Slider((TIMEOUT, 100), k='timeOut', size=(0, 10), orientation='h', expand_x=True), sg.Text('Sensitivity:'), sg.Slider((100, 2000), 800, k='area', size=(0, 10), orientation='h', expand_x=True)],
        [sg.Text('Person trigger:'), sg.Slider((50, 500), 75, k='person', size=(0, 10), orientation='h', expand_x=True), sg.Text('Sound Nº'), sg.Combo(audios, default_value=audios[20], s=(10, 0), k='audio_index')],
        [sg.Button('Play Audio', k='snd',button_color='green', size=(0, 2), expand_x=True), sg.Button('Reset trigger', k='trigger', size=(0, 2), expand_x=True)],
        [sg.Image(filename='', key='image')]
    ]
    window = sg.Window('Tortops Vending', layout, size=(550, 900), resizable=True, keep_on_top=True)
    while True:
        event, values = window.read(timeout=round(1000 / 15))
        if event == 'startBtn':
            if screenViewer.is_running:
                screenViewer.stop(int(values['timeOut']))
                window['startBtn'].update('Start')
            else:
                screenViewer.start(int(values['timeOut']))
                window['startBtn'].update('Running')

        elif event == 'snd':
            if screenViewer.switch_play_sound():
                window['snd'].update(button_color='green')
                screenViewer.switch_play_sound(True)
            else:
                window['snd'].update(button_color='red')
                screenViewer.switch_play_sound(False)
        elif event == 'trigger':
            if screenViewer.is_running:
                screenViewer.reset_trigger(int(values['timeOut']))
                window.ding()
                window['startBtn'].update('Running')
        elif event == sg.WIN_CLOSED or event == 'Exit':
            break
        if screenViewer.is_running:
            if screenViewer.triggered is True:
                if not screenRecorder.is_recording():
                    screenRecorder.start_recording()
                window['startBtn'].update(f'Waiting {screenViewer.timeout / 5} seg')
                screenViewer.timeout -= 1
                if screenViewer.timeout <= 0:
                    window['startBtn'].update('Running')
                    screenViewer.triggered = False
                    screenViewer.timeout = int(values['timeOut']) * 5
                    window.ding()
            else:
                if screenRecorder.is_recording():
                    screenRecorder.stop_recording()
        screenViewer.audio = int(values['audio_index'])
        x1, y1 = window.current_location()
        x2, y2 = window.current_location()
        x2_offset, y2_offset = window.current_size_accurate()
        x_offset = x2_offset
        y_offset = 210
        imgbytes = screenViewer.run_window(int(values['area']), (x1 - x_offset, y1 + y_offset, x2 + x2_offset - x_offset, y2 + y2_offset), int(values['person']))
        window['image'].update(data=imgbytes)
        window.set_title(f'V.{version} Triggered: {screenViewer.triggered}, Timeout: {screenViewer.timeout}, person (?: {screenViewer.is_person}')
    window.close()


if __name__ == "__main__":
    main()
