"""
фрейм с операциями, копирование .....
"""

from tkinter import Frame, SOLID, Button, X, messagebox

import os


class OperationsFrame(Frame):

    def __init__(self, parent, left, right, debug=False):
        super(OperationsFrame, self).__init__(parent)

        self.debug = debug

        self.w_left = left
        self.w_right = right

        self.w_button = Button(self, text='Сравнить', command=self.compare)

    def w_config(self):
        """
        конфигурация виджетов
        :return:
        """
        self.configure(
            borderwidth=1,
            relief=SOLID,
        )

    def w_layout(self):
        """
        распологаем виджеты
        :return:
        """
        self.w_button.pack(fill=X)

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
        try:
            listdir = os.listdir(path)
        except Exception as err:
            messagebox.showerror('Error', str(err))
        else:            
            for fl in listdir:
                fl_path = os.path.join(path, fl)
                if not os.path.exists(fl_path):
                    continue
                if os.path.isdir(fl_path):
                    _files, _count, _size = self.get_dir_stat(fl_path)
                    count += _count
                    size += _size
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

        return files_dict, count, size

    def compare(self):
        root_left = self.w_left.var_current_path.get()
        files_dict_left, count_left, size_left = self.get_dir_stat(root_left, True)

        root_right = self.w_right.var_current_path.get()
        files_dict_right, count_right, size_right = self.get_dir_stat(root_right, True)

        self.w_left.var_counts.set('{0}/{1}'.format(count_left, size_left))
        self.w_right.var_counts.set('{0}/{1}'.format(count_right, size_right))

        for w_1, w_2, f_d_1, f_d_2 in (
                (self.w_left, self.w_right, files_dict_left, files_dict_right),
                (self.w_right, self.w_left, files_dict_right, files_dict_left)
        ):
            for fl, size in f_d_1.items():
                if fl not in f_d_2:
                    item_index = w_1.listbox_items.index(fl)
                    w_1.w_listbox.itemconfig(item_index, bg='green')
                elif f_d_2[fl] != size:
                    item_index = w_1.listbox_items.index(fl)
                    w_1.w_listbox.itemconfig(item_index, bg='red')
