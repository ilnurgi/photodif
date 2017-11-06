from tkinter import Tk, messagebox

import os
import shutil

from cmpframe import CmpFrame
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

        cmp_frame_w = 0.5

        w_left_frame_x = 0
        w_left_frame_y = 0
        w_left_frame_h = 1
        w_left_frame_w = cmp_frame_w

        w_right_frame_x = cmp_frame_w
        w_right_frame_y = 0
        w_right_frame_h = 1
        w_right_frame_w = cmp_frame_w

        self.w_left_frame.place(
            relx=w_left_frame_x,
            rely=w_left_frame_y,
            relwidth=w_left_frame_w,
            relheight=w_left_frame_h)

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

    def get_dir_stat(self, path, files=False):
        """
        рекурсивный сборщик статистики
        :param path:
        :param files:
        :return:
        """
        # количество объектов в папка
        count = 0
        # общий размер объектов
        size = 0
        # объекты в папке
        files_dict = {}
        # ошибки
        errors = []
        try:
            listdir = os.listdir(path)
        except Exception as err:
            errors.append(str(err))
        else:
            for fl in listdir:
                fl_path = os.path.join(path, fl)
                if not os.path.exists(fl_path):
                    continue
                if os.path.isdir(fl_path):
                    _files, _count, _size, _errors = self.get_dir_stat(fl_path)
                    count += _count
                    size += _size
                    errors.extend(_errors)
                    if files:
                        files_dict[fl] = {
                            'size': _size,
                            'count': _count
                        }
                else:
                    count += 1
                    _size = os.stat(fl_path).st_size
                    size += _size
                    if files:
                        files_dict[fl] = {
                            'size': _size,
                            'count': 1
                        }

        return files_dict, count, size, errors

    def compare(self):
        """
        сравнивает списки файлов
        """
        self.w_left_frame.load_list()
        self.w_right_frame.load_list()

        root_left = self.w_left_frame.var_current_path.get()
        files_dict_left, count_left, size_left, errors_left = self.get_dir_stat(root_left, True)

        root_right = self.w_right_frame.var_current_path.get()
        files_dict_right, count_right, size_right, errors_right = self.get_dir_stat(root_right, True)

        self.w_left_frame.var_counts.set('{0}/{1}'.format(count_left, size_left))
        self.w_right_frame.var_counts.set('{0}/{1}'.format(count_right, size_right))

        for w_1, w_2, f_d_1, f_d_2 in (
                (self.w_left_frame, self.w_right_frame, files_dict_left, files_dict_right),
                (self.w_right_frame, self.w_left_frame, files_dict_right, files_dict_left)
        ):
            for fl, size in f_d_1.items():
                if fl not in f_d_2:
                    item_index = w_1.listbox_items.index(fl)
                    w_1.w_listbox.itemconfig(item_index, bg='green')
                elif f_d_2[fl] != size:
                    item_index = w_1.listbox_items.index(fl)
                    w_1.w_listbox.itemconfig(item_index, bg='red')

        errors_left.extend(errors_right)
        if errors_left:
            messagebox.showerror('Errors', '\n'.join(errors_left))
        else:
            messagebox.showinfo('Compare', 'DONE')

    def copy_file(self, frame, selected_file_name):
        """
        копирует файл из одного фрейма в другой
        """
        if frame == self.w_left_frame:
            src = os.path.join(self.w_left_frame.var_current_path.get(), selected_file_name)
            dst = os.path.join(self.w_right_frame.var_current_path.get(), selected_file_name)
        elif frame == self.w_right_frame:
            src = os.path.join(self.w_right_frame.var_current_path.get(), selected_file_name)
            dst = os.path.join(self.w_left_frame.var_current_path.get(), selected_file_name)
        else:
            return

        if messagebox.askyesno(
            'Копирование',
            'Из\n{0}\nв\n{1}'.format(src, dst)
        ):
            if os.path.exists(dst):
                messagebox.showerror(
                    'Ошибка при копировании',
                    'Указанный файл уже существует\n'.format(dst)
                )
            else:
                try:
                    shutil.copy2(src, dst)
                except Exception as err:
                    messagebox.showerror(
                        'Ошибка при копировании',
                        str(err)
                    )
                else:
                    frame.load_list()

app = App()
app.start()
app.destroy()
