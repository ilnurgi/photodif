"""
фрейм окна для вывода списка файлов и переименовании
"""

import os
import shutil
import string
import subprocess

from datetime import datetime
from tkinter import (
    Frame, SOLID, Listbox, Label, StringVar, END, Scrollbar, SINGLE, messagebox, OptionMenu, Button, Menu, simpledialog, EXTENDED)

from PIL import Image, ImageTk, ExifTags

from settings import AVAILABLE_FILE_ENDS, DATE_TIME_FORMAT, DATE_TIME_FORMAT_EXIF, DATE_TIME_FORMAT_NEW_FILE

EXIF_TAGS = {v: k for k, v in ExifTags.TAGS.items()}


class CmpFrame(Frame):

    def __init__(self, parent, app, start_path, debug=False):
        super(CmpFrame, self).__init__(parent)

        self.app = app
        self.debug = debug
        self.listbox_items = []
        self.current_image_path = None

        self.var_dt_create = StringVar(value='')
        self.var_dt_modify = StringVar(value='')
        self.var_dt_original = StringVar(value='')
        self.var_dt_digitized = StringVar(value='')
        self.var_dt = StringVar(value='')
        self.var_counts = StringVar(value='')

        self.var_dt_create_new = StringVar(value='')
        self.var_dt_modify_new = StringVar(value='')
        self.var_dt_original_new = StringVar(value='')
        self.var_dt_digitized_new = StringVar(value='')
        self.var_dt_new = StringVar(value='')

        self.var_current_path = StringVar(value='')
        self.var_current_file = StringVar(value='')
        self.var_current_path_root = StringVar()
        roots = []
        for i in string.ascii_lowercase:
            path = '{0}:\\'.format(i)
            if os.path.exists(path):
                roots.append(path)
                if start_path.lower().startswith(i):
                    self.var_current_path_root.set(i)

        for _ in range(5):
            if os.path.exists(start_path):
                self.var_current_path.set(start_path)
            else:
                start_path = os.path.dirname(start_path)

        self.w_listbox = Listbox(self, selectmode=EXTENDED)
        self.w_label_current_path = Label(self, textvariable=self.var_current_path)
        self.w_label_image = Label(self)
        self.w_scrollbar = Scrollbar(self)
        self.w_option_menu = OptionMenu(self, self.var_current_path_root, *roots, command=self.current_path_root_change)
        self.w_label_counts = Label(self, textvariable=self.var_counts)

        self.w_lbl_dt_create = Label(self, text='Создание')
        self.w_lbl_dt_modify = Label(self, text='Изменение')
        self.w_lbl_dt_original = Label(self, text='Original')
        self.w_lbl_dt_digitized = Label(self, text='Digitized')
        self.w_lbl_dt = Label(self, text='DateTime')

        self.w_lbl_dt_create_2 = Label(self, textvariable=self.var_dt_create)
        self.w_lbl_dt_modify_2 = Label(self, textvariable=self.var_dt_modify)
        self.w_lbl_dt_original_2 = Label(self, textvariable=self.var_dt_original)
        self.w_lbl_dt_digitized_2 = Label(self, textvariable=self.var_dt_digitized)
        self.w_lbl_dt_2 = Label(self, textvariable=self.var_dt)

        self.w_lbl_dt_create_new = Label(self, textvariable=self.var_dt_create_new)
        self.w_lbl_dt_modify_new = Label(self, textvariable=self.var_dt_modify_new)
        self.w_lbl_dt_original_new = Label(self, textvariable=self.var_dt_original_new)
        self.w_lbl_dt_digitized_new = Label(self, textvariable=self.var_dt_digitized_new)
        self.w_lbl_dt_new = Label(self, textvariable=self.var_dt_new)

        self.w_btn_dt_create = Button(self, text='Переименовать в ->')
        self.w_btn_dt_modify = Button(self, text='Переименовать в ->')
        self.w_btn_dt_original = Button(self, text='Переименовать в ->')
        self.w_btn_dt_digitized = Button(self, text='Переименовать в ->')
        self.w_btn_dt = Button(self, text='Переименовать в ->')

        self.w_popup = Menu(self)
        self.w_popup.add_command(
            label='Открыть файл',
            command=lambda: subprocess.call(
                ['open',
                '"{0}"'.format(
                    os.path.join(self.var_current_path.get(), self.var_current_file.get()))]))
        self.w_popup.add_command(
            label='Открыть папку',
            command=lambda: subprocess.call(
                ['explorer', self.var_current_path.get()]))
        self.w_popup.add_command(
            label='Показать файл в папке',
            command=lambda: subprocess.call(
                ['explorer',
                 '/select,',
                 os.path.join(self.var_current_path.get(), self.var_current_file.get())]))
        self.w_popup.add_separator()
        self.w_popup.add_command(label='Переименовать', command=self.rename_custom)
        self.w_popup.add_command(label='Копировать', command=self.copy_file)
        self.w_popup.add_command(label='Удалить', command=self.remove_file)
        self.w_popup.add_separator()
        self.w_popup.add_command(label='Переименовать массово из ORIGINAL', command=self.rename_all_original)
        self.w_popup.add_separator()
        self.w_popup.add_command(label='Сравнить', command=self.app.compare)

        self.load_list()

    def w_config(self):
        """
        конфигурация виджетов
        :return:
        """
        if self.debug:
            self.configure(
                borderwidth=2,
                relief=SOLID
            )
            self.w_listbox.configure(
                borderwidth=2,
                relief=SOLID,
                highlightbackground='blue'
            )
            self.w_label_image.configure(
                borderwidth=2,
                relief=SOLID,
                highlightbackground='blue'
            )
            self.w_lbl_dt_create.configure(
                borderwidth=2,
                relief=SOLID,
                highlightbackground='blue'
            )
            self.w_lbl_dt_modify.configure(
                borderwidth=2,
                relief=SOLID,
                highlightbackground='blue'
            )
            self.w_lbl_dt_original.configure(
                borderwidth=2,
                relief=SOLID,
                highlightbackground='blue'
            )
            self.w_lbl_dt_digitized.configure(
                borderwidth=2,
                relief=SOLID,
                highlightbackground='blue'
            )
            self.w_lbl_dt.configure(
                borderwidth=2,
                relief=SOLID,
                highlightbackground='blue'
            )
            self.w_lbl_dt_2.configure(
                borderwidth=2,
                relief=SOLID,
                highlightbackground='blue'
            )
            self.w_lbl_dt_new.configure(
                borderwidth=2,
                relief=SOLID,
                highlightbackground='blue'
            )

        self.w_listbox.config(
            yscrollcommand=self.w_scrollbar.set,
        )
        self.w_listbox.bind(
            '<Double-Button-1>', self.current_path_change)

        self.w_listbox.bind(
            '<<ListboxSelect>>', self.current_image_change)

        self.w_listbox.bind(
            '<Button-3>', self.popup)

        self.w_scrollbar.config(
            command=self.w_listbox.yview,
        )

        self.w_btn_dt.bind(
            '<Button-1>', self.rename)
        self.w_btn_dt_create.bind(
            '<Button-1>', self.rename)
        self.w_btn_dt_digitized.bind(
            '<Button-1>', self.rename)
        self.w_btn_dt_modify.bind(
            '<Button-1>', self.rename)
        self.w_btn_dt_original.bind(
            '<Button-1>', self.rename)

    def w_layout(self):
        """
        распологаем виджеты
        :return:
        """

        w_om_w = 0.1
        w_om_h = 0.03

        w_label_cp_x = w_om_w
        w_label_cp_w = 0.7
        w_label_cp_h = w_om_h

        #w_lb_image_y = w_om_h + w_lb_h
        w_lb_image_y = w_om_h
        w_lb_image_h = 0.5

        w_lb_y = w_lb_image_y + w_lb_image_h
        w_lb_w = 0.98
        w_lb_h = 0.3

        w_sb_x = w_lb_w
        w_sb_y = w_lb_y
        w_sb_w = 1 - w_lb_w
        w_sb_h = w_lb_h

        w_lbl_dt_w = 0.14
        w_lbl_dt_h = 0.034

        w_lbl_dt_y1 = w_lb_y + w_lb_h

        w_btn_w = 0.2

        w_lbl_dt_new_x = w_btn_w + w_lbl_dt_w * 3
        w_lbl_dt_new_w = 1 - w_lbl_dt_new_x

        self.w_option_menu.place(
            relx=0,
            rely=0,
            relwidth=w_om_w,
            relheight=w_om_h,
        )
        self.w_label_current_path.place(
            relx=w_label_cp_x,
            rely=0,
            relwidth=w_label_cp_w,
            relheight=w_label_cp_h,
        )
        self.w_label_counts.place(
            relx=w_om_w + w_label_cp_w,
            rely=0,
            relwidth=1 - (w_om_w + w_label_cp_w),
            relheight=w_om_h
        )
        self.w_listbox.place(
            relx=0,
            rely=w_lb_y,
            relwidth=w_lb_w,
            relheight=w_lb_h,
        )
        self.w_scrollbar.place(
            relx=w_sb_x,
            rely=w_sb_y,
            relwidth=w_sb_w,
            relheight=w_sb_h,
        )
        self.w_label_image.place(
            relx=0,
            rely=w_lb_image_y,
            relwidth=1,
            relheight=w_lb_image_h,
        )
        self.w_lbl_dt_create.place(
            relx=0,
            rely=w_lbl_dt_y1,
            relwidth=w_lbl_dt_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_modify.place(
            relx=0,
            rely=w_lbl_dt_y1 + w_lbl_dt_h,
            relwidth=w_lbl_dt_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_original.place(
            relx=0,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 2,
            relwidth=w_lbl_dt_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_digitized.place(
            relx=0,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 3,
            relwidth=w_lbl_dt_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt.place(
            relx=0,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 4,
            relwidth=w_lbl_dt_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_create_2.place(
            relx=w_lbl_dt_w,
            rely=w_lbl_dt_y1,
            relwidth=w_lbl_dt_w * 2,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_modify_2.place(
            relx=w_lbl_dt_w,
            rely=w_lbl_dt_y1 + w_lbl_dt_h,
            relwidth=w_lbl_dt_w * 2,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_original_2.place(
            relx=w_lbl_dt_w,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 2,
            relwidth=w_lbl_dt_w * 2,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_digitized_2.place(
            relx=w_lbl_dt_w,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 3,
            relwidth=w_lbl_dt_w * 2,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_2.place(
            relx=w_lbl_dt_w,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 4,
            relwidth=w_lbl_dt_w * 2,
            relheight=w_lbl_dt_h,
        )
        self.w_btn_dt_create.place(
            relx=w_lbl_dt_w * 3,
            rely=w_lbl_dt_y1,
            relwidth=w_btn_w,
            relheight=w_lbl_dt_h,
        )
        self.w_btn_dt_modify.place(
            relx=w_lbl_dt_w * 3,
            rely=w_lbl_dt_y1 + w_lbl_dt_h,
            relwidth=w_btn_w,
            relheight=w_lbl_dt_h,
        )
        self.w_btn_dt_original.place(
            relx=w_lbl_dt_w * 3,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 2,
            relwidth=w_btn_w,
            relheight=w_lbl_dt_h,
        )
        self.w_btn_dt_digitized.place(
            relx=w_lbl_dt_w * 3,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 3,
            relwidth=w_btn_w,
            relheight=w_lbl_dt_h,
        )
        self.w_btn_dt.place(
            relx=w_lbl_dt_w * 3,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 4,
            relwidth=w_btn_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_create_new.place(
            relx=w_lbl_dt_new_x,
            rely=w_lbl_dt_y1,
            relwidth=w_lbl_dt_new_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_modify_new.place(
            relx=w_lbl_dt_new_x,
            rely=w_lbl_dt_y1 + w_lbl_dt_h,
            relwidth=w_lbl_dt_new_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_original_new.place(
            relx=w_lbl_dt_new_x,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 2,
            relwidth=w_lbl_dt_new_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_digitized_new.place(
            relx=w_lbl_dt_new_x,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 3,
            relwidth=w_lbl_dt_new_w,
            relheight=w_lbl_dt_h,
        )
        self.w_lbl_dt_new.place(
            relx=w_lbl_dt_new_x,
            rely=w_lbl_dt_y1 + w_lbl_dt_h * 4,
            relwidth=w_lbl_dt_new_w,
            relheight=w_lbl_dt_h,
        )

    def load_list(self, path=None):
        """
        загружает список для списка файлов
        """
        current_path = path or self.var_current_path.get()

        try:
            list_dir = os.listdir(current_path)
        except PermissionError as err:
            messagebox.showerror('PermissionError', str(err))
            return False
        else:
            items_list = []
            files = []
            for item in list_dir:
                if os.path.isdir(os.path.join(current_path, item)):
                    items_list.append(item)
                else:
                    files.append(item)
            items_list.extend(files)

        self.listbox_items = ['...']
        self.listbox_items.extend(items_list)

        self.w_listbox.delete(0, END)
        self.w_listbox.insert(END, *self.listbox_items)
        self.var_counts.set('')

        return True

    def current_path_change(self, event):
        """
        обработчик двойного клика по списку файлов
        """
        selected_items = self.w_listbox.curselection()

        if selected_items:
            selected_index = selected_items[0]

            if selected_index != 0:
                path = os.path.join(
                    self.var_current_path.get(),
                    self.listbox_items[selected_index]
                )
            else:
                path = os.path.join(
                    os.path.dirname(
                        self.var_current_path.get(),
                    )
                )
                for _ in range(5):
                    if os.path.exists(path):
                        break
                    path = os.path.dirname(path)

            if os.path.isdir(path):
                if self.load_list(path):
                    self.var_current_path.set(path)
                    self.reset_renames()
                    self.current_image_change(None)
            else:
                subprocess.call(
                    ['explorer',
                     os.path.join(self.var_current_path.get(), self.var_current_file.get())])

    def current_image_change(self, event):
        """
        обработчик выбора элемента в списке
        """
        self.reset_renames()
        if event is None:
            self.set_image(None)
            return

        self.var_current_file.set('')
        selected_index, selected_file_name = self.get_selected_item()
        if selected_index and selected_file_name:
            path = os.path.join(
                self.var_current_path.get(),
                selected_file_name
            )
            if os.path.isfile(path):
                self.var_current_file.set(selected_file_name)
                if any(selected_file_name.lower().endswith(ext) for ext in AVAILABLE_FILE_ENDS):                
                    self.set_image(path)                      
                else:            
                    stat = os.stat(path)
                    self.var_dt_create.set(datetime.fromtimestamp(stat.st_ctime).strftime(DATE_TIME_FORMAT))
                    self.var_dt_modify.set(datetime.fromtimestamp(stat.st_mtime).strftime(DATE_TIME_FORMAT))
                    for dt_from, dt_to in (
                            (self.var_dt_create, self.var_dt_create_new),
                            (self.var_dt_modify, self.var_dt_modify_new),
                    ):
                        try:
                            rename_name = datetime.strptime(
                                dt_from.get(), DATE_TIME_FORMAT
                            ).strftime(DATE_TIME_FORMAT_NEW_FILE)
                        except ValueError:
                            try:
                                rename_name = datetime.strptime(
                                    dt_from.get(), DATE_TIME_FORMAT_EXIF
                                ).strftime(
                                    DATE_TIME_FORMAT_NEW_FILE)
                            except ValueError:
                                rename_name = None

                        if rename_name:
                            rename_name = '{0}_{1}{2}'.format(
                                rename_name,
                                stat.st_size,
                                os.path.splitext(path)[-1]
                            )
                            dt_to.set(rename_name)

    def current_path_root_change(self, new_value):
        """
        устанавливает новый раздел папок
        """

        if os.path.isdir(new_value):
            if self.load_list(new_value):
                self.var_current_path.set(new_value)
                self.reset_renames()

    def get_image_exif_dates(self, path: str or None):
        """
        возвращает объект изображения и даты из ексиф
        """
        image = dt_original = dt_digitized = dt = None

        if path is None:
            self.w_label_image.config(image=None)
            self.w_label_image.image = None
        else:
            try:
                image = Image.open(path)
            except IOError:
                self.w_label_image.config(image=None)
                self.w_label_image.image = None
            else:
                try:
                    exif_data = image._getexif()
                except AttributeError:
                    exif_data = None
                if exif_data:
                    dt_original = exif_data.get(EXIF_TAGS['DateTimeOriginal'])
                    dt_digitized = exif_data.get(EXIF_TAGS['DateTimeDigitized'])
                    dt = exif_data.get(EXIF_TAGS['DateTime'])

        return image, dt_original, dt_digitized, dt

    def get_rename_name(self, dt, size, path):
        """
        возвращает имя для переименования
        """
        try:
            rename_name = datetime.strptime(
                dt, DATE_TIME_FORMAT
            ).strftime(DATE_TIME_FORMAT_NEW_FILE)
        except ValueError:
            try:
                rename_name = datetime.strptime(
                    dt, DATE_TIME_FORMAT_EXIF
                ).strftime(
                    DATE_TIME_FORMAT_NEW_FILE)
            except ValueError:
                rename_name = None
        except TypeError:
            rename_name = None

        if rename_name:
            rename_name = '{0}_{1}{2}'.format(
                rename_name,
                size,
                os.path.splitext(path)[-1]
            )
        return rename_name

    def set_image(self, path):
        """
        грузим картинку на форму
        """

        image, date_exif_original, date_exif_digitized, date_exif = self.get_image_exif_dates(path)

        if path is not None:
            stat = os.stat(path)
            self.var_dt_create.set(datetime.fromtimestamp(stat.st_ctime).strftime(DATE_TIME_FORMAT))
            self.var_dt_modify.set(datetime.fromtimestamp(stat.st_mtime).strftime(DATE_TIME_FORMAT))

        if image is None:
            self.w_label_image.config(image=None)
            self.w_label_image.image = None
            return 

        height = self.w_label_image.winfo_height()
        width = self.w_label_image.winfo_width()

        image_width, image_height = image.size
        if image_height > height:
            percent = height / float(image_height)
            width = int(image_width * percent)
        elif image_width > width:
            percent = width / float(image_width)
            height = int(image_height * percent)

        image_photo = ImageTk.PhotoImage(
            image.resize((width, height), Image.ANTIALIAS))
        self.w_label_image.config(
            image=image_photo
        )
        self.w_label_image.image = image_photo

        self.var_dt_original.set(date_exif_original or u'---')
        self.var_dt_digitized.set(date_exif_digitized or u'---')
        self.var_dt.set(date_exif or u'---')

        for dt_from, dt_to in (
                (self.var_dt_digitized, self.var_dt_digitized_new),
                (self.var_dt_original, self.var_dt_original_new),
                (self.var_dt, self.var_dt_new),
                (self.var_dt_create, self.var_dt_create_new),
                (self.var_dt_modify, self.var_dt_modify_new),
        ):
            rename_name = self.get_rename_name(dt_from.get(), stat.st_size, path)
            if rename_name:
                dt_to.set(rename_name)

        return True

    def rename(self, event):
        w_btn = event.widget

        if w_btn == self.w_btn_dt_create:
            name_dst = self.var_dt_create_new.get()
        elif w_btn == self.w_btn_dt_modify:
            name_dst = self.var_dt_modify_new.get()
        elif w_btn == self.w_btn_dt_digitized:
            name_dst = self.var_dt_digitized_new.get()
        elif w_btn == self.w_btn_dt_original:
            name_dst = self.var_dt_original_new.get()
        elif w_btn == self.w_btn_dt_create:
            name_dst = self.var_dt_new.get()
        else:
            name_dst = ''

        name_src = self.var_current_file.get()
        if not name_src or not name_dst:
            return

        src = os.path.join(self.var_current_path.get(), name_src)
        dst = os.path.join(self.var_current_path.get(), name_dst)
        self.rename_file(src, dst)
        self.load_list()

    def popup(self, event):
        """
        отображаем контекстное меню
        :param event:
        :return:
        """
        try:
            self.w_popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.w_popup.grab_release()

    def reset_renames(self):
        """
        сбрасывает переменные для переименования
        :return:
        """
        self.var_dt_create.set('')
        self.var_dt_modify.set('')
        self.var_dt_original.set('')
        self.var_dt_digitized.set('')
        self.var_dt.set('')

        self.var_dt_create_new.set('')
        self.var_dt_modify_new.set('')
        self.var_dt_original_new.set('')
        self.var_dt_digitized_new.set('')
        self.var_dt_new.set('')

    def rename_custom(self):
        """
        частное переименование
        :param event:
        :return:
        """
        selected_index, selected_file_name = self.get_selected_item()
        if selected_index and selected_file_name:
            new_val = simpledialog.askstring('Введите новое название для файла', selected_file_name)
            if new_val:
                src = os.path.join(self.var_current_path.get(), selected_file_name)
                dst = os.path.join(self.var_current_path.get(), new_val)
                self.rename_file(src, dst)
                self.load_list()

    def get_selected_item(self):
        """
        возвращает выбранный индекс и название файла
        :return:
        """
        selected_index = selected_file_name = None

        selected_items = self.w_listbox.curselection()

        if selected_items:
            selected_index = selected_items[0]

            if selected_index != 0:
                selected_file_name = self.listbox_items[selected_index]

        return selected_index, selected_file_name

    def get_selected_items(self) -> list:
        """
        возвращает список выбранных названий файлов
        """
        return [
            self.listbox_items[selected_index]
            for selected_index in self.w_listbox.curselection()
            if selected_index != 0
        ]

    def rename_file(self, src, dst):
        if messagebox.askyesno(
            'Переименовать файл',
            'Вы уверены?\n{0}\n{1}'.format(src, dst)
        ):
            if os.path.exists(dst):
                messagebox.showerror(
                    'Ошибка переименования',
                    'Файл ({0}) уже существует'.format(dst))
            else:
                try:
                    os.rename(src, dst)
                except Exception as err:
                    messagebox.showerror(
                        'Ошибка переименования',
                        str(err))

    def copy_file(self):
        """
        копирует выбранные файлы
        """
        for selected_file_name in self.get_selected_items():
            self.app.copy_file(self, selected_file_name)

    def remove_file(self):
        """
        удаялет файл
        """
        selected_index, selected_file_name = self.get_selected_item()
        if selected_index:
            path = os.path.join(self.var_current_path.get(), selected_file_name)
            if os.path.exists(path):
                if os.path.isdir(path):
                    if messagebox.askyesno(
                        'Удаление папки',
                        'Удалить ПАПКУ?\n{0}'.format(path)
                    ):
                        try:
                            shutil.rmtree(path)
                        except Exception as err:
                            messagebox.showerror(
                                'Удаление папки',
                                str(err)
                            )
                        else:
                            self.load_list()
                elif os.path.isfile(path):
                    if messagebox.askyesno(
                        'Удаление файла',
                        'Удалить файл?\n{0}'.format(path)
                    ):
                        try:
                            os.remove(path)
                        except Exception as err:
                            messagebox.showerror(
                                'Удаление папки',
                                str(err)
                            )
                        else:
                            self.load_list()
            else:
                messagebox.showerror(
                    'Удаление объекта',
                    'Объекта не существует\n{0}'.format(path)
                )

    def rename_all_original(self):
        """
        массовое переименование из original
        """
        for index in self.w_listbox.curselection():
            try:
                selected_item = self.listbox_items[index]
            except IndexError as err:
                messagebox.showerror(
                    'Ошибка',
                    str(err)
                )
            else:
                src = os.path.join(self.var_current_path.get(), selected_item)
                image, dt_original, dt_digitized, dt = self.get_image_exif_dates(src)  
                # необходимо освобождать файл, чтобы была возможность его переименовать
                del image
                rename_name = self.get_rename_name(
                    dt_original, 
                    os.stat(src).st_size,
                    src)
                if rename_name:                
                    self.rename_file(
                        src,
                        os.path.join(self.var_current_path.get(), rename_name)
                    )
        self.load_list()
