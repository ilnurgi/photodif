from tkinter import Tk

from cmpframe import CmpFrame
from operframe import OperationsFrame
from settings import DEBUG, DIR_START_LEFT, DIR_START_RIGHT, write as settings_write, VERSION, SOFT_NAME


class App(object):
    """
    приложение
    """

    def __init__(self):
        """
        инициализация приложения
        """
        self.w_window = Tk()

        self.w_left_frame = CmpFrame(self.w_window, self, debug=DEBUG, start_path=DIR_START_LEFT)
        self.w_right_frame = CmpFrame(self.w_window, self, debug=DEBUG, start_path=DIR_START_RIGHT)
        self.w_center_frame = OperationsFrame(self.w_window, self.w_left_frame, self.w_right_frame, debug=DEBUG)

        self.w_window_width_max = None
        self.w_window_height_max = None

    def configure_event(self, event):
        """
        обработка событий изменений конфигурации окна
        :param event:
        :return:
        """
        if self.w_window_height_max is None:
            self.w_window_width_max = self.w_window.winfo_width()
            self.w_window_height_max = self.w_window.winfo_height()
            self.w_window.minsize(self.w_window_width_max, self.w_window_height_max)

    def w_config(self):
        """
        настройка виджетов и окна
        :return:
        """
        self.w_left_frame.w_config()
        self.w_right_frame.w_config()
        self.w_center_frame.w_config()

        self.w_window.wm_state('zoomed')
        self.w_window.title('{0}: {1}'.format(SOFT_NAME, VERSION))
        self.w_window.bind("<Configure>", self.configure_event)

    def w_layout(self):
        """
        раскидываем виджеты по окну
        :return:
        """
        self.w_left_frame.w_layout()
        self.w_right_frame.w_layout()
        self.w_center_frame.w_layout()

        cmp_frame_w = 0.45

        w_left_frame_x = 0
        w_left_frame_y = 0
        w_left_frame_h = 1
        w_left_frame_w = cmp_frame_w

        w_center_frame_x = w_left_frame_w
        w_center_frame_y = 0
        w_center_frame_h = 1
        w_center_frame_w = 1 - 2 * cmp_frame_w

        w_right_frame_x = w_left_frame_w + w_center_frame_w
        w_right_frame_y = 0
        w_right_frame_h = 1
        w_right_frame_w = cmp_frame_w

        self.w_left_frame.place(
            relx=w_left_frame_x,
            rely=w_left_frame_y,
            relwidth=w_left_frame_w,
            relheight=w_left_frame_h)

        self.w_center_frame.place(
            relx=w_center_frame_x,
            rely=w_center_frame_y,
            relwidth=w_center_frame_w,
            relheight=w_center_frame_h)

        self.w_right_frame.place(
            relx=w_right_frame_x,
            rely=w_right_frame_y,
            relwidth=w_right_frame_w,
            relheight=w_right_frame_h)

    def destroy(self):
        """
        обработчик закрытия программы
        """
        settings_write(
            DIR_START_LEFT=self.w_left_frame.var_current_path.get(),
            DIR_START_RIGHT=self.w_right_frame.var_current_path.get(),
        )

    def start(self):
        """
        запуск приложения
        :return:
        """
        self.w_config()
        self.w_layout()
        self.w_window.mainloop()


app = App()
app.start()
app.destroy()
