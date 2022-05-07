from recorder import Screenwindow
import PySimpleGUI as sg


def main():
    screenViewer = Screenwindow(200)
    layout = [
        [sg.Button('Start', k='OffButton', size=(0, 3), expand_x=True)],
        [sg.Input('50', k='timeOut', size=(0, 2), expand_x=True), sg.Input('3500', k='area', size=(0, 2), expand_x=True)],
        [sg.Button('Enable Sound', k='snd', size=(0, 2), expand_x=True), sg.Button('Reset trigger', k='trigger', size=(0, 2), expand_x=True)],
        [sg.Image(filename='', key='image')]
    ]
    window = sg.Window('Tortops Vending', layout, size=(400, 400), resizable=True, keep_on_top=True)

    def time_out(count=0):
        if count <= 0:
            return True
        return count - 1


    while True:
        event, values = window.read(timeout=round(1000 / 15))
        if event == 'OffButton':
            if screenViewer.is_running:
                screenViewer.stop()
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
            screenViewer.reset_trigger()
            window.ding()
            window['OffButton'].update('Running')
        elif event == sg.WIN_CLOSED or event == 'Exit':
            break
        if screenViewer.is_running:
            if screenViewer.triggered is True:
                window['OffButton'].update(f'Waiting {screenViewer.timeout/5} seg')
                screenViewer.timeout -= 1
                if screenViewer.timeout <= 0:
                    window['OffButton'].update('Running')
                    screenViewer.triggered = False
                    screenViewer.timeout = int(values['timeOut']) * 5
                    window.ding()
        x1, y1 = window.current_location()
        x2, y2 = window.current_location()
        x2_offset, y2_offset = window.current_size_accurate()
        offset = x2_offset
        imgbytes = screenViewer.run_window(area_pixels=int(values['area']), bounding_box=(x1 - offset, y1, x2 + x2_offset - offset, y2 + y2_offset))
        window['image'].update(data=imgbytes)
        window.set_title(f'Triggered: {screenViewer.triggered}, Timeout: {screenViewer.timeout}, boxes: {len(screenViewer.detections)}')
    window.close()


if __name__ == "__main__":
    main()
