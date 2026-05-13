from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.list import OneLineListItem
from kivy.properties import StringProperty, DictProperty, BooleanProperty
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivymd.uix.filemanager import MDFileManager
from kivy.clock import Clock
import webbrowser
import json
import os
import threading
from urllib.request import urlopen, Request

KV = '''
ScreenManager:
    id: screen_manager

    MDScreen:
        name: "menu"

        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Лабораторные работы"

            MDBoxLayout:
                id: last_lab_box
                orientation: "vertical"
                adaptive_height: True
                padding: "10dp"
                spacing: "5dp"
                opacity: 0 if not app.last_opened_lab else 1
                disabled: not app.last_opened_lab
                MDLabel:
                    text: "Последняя открытая:"
                    font_style: "Caption"
                    halign: "center"
                MDRaisedButton:
                    text: app.last_opened_lab if app.last_opened_lab else ""
                    size_hint_x: 0.8
                    pos_hint: {"center_x": .5}
                    on_release: app.continue_last_lab()

            AnchorLayout:
                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    spacing: "20dp"
                    MDRaisedButton:
                        text: "ФИЗИКА"
                        size_hint: (0.8, None)
                        pos_hint: {"center_x": .5}
                        on_release:
                            app.current_subject = "physics"
                            app.root.current = "physics_list"
                    MDRaisedButton:
                        text: "ХИМИЯ"
                        size_hint: (0.8, None)
                        pos_hint: {"center_x": .5}
                        on_release:
                            app.current_subject = "chemistry"
                            app.root.current = "chemistry_list"

        MDFloatingActionButton:
            icon: "cog"
            pos_hint: {"right": 0.95, "y": 0.05}
            on_release: app.root.current = "settings"

    MDScreen:
        name: "settings"
        MDBoxLayout:
            orientation: "vertical"
            MDTopAppBar:
                title: "Настройки"
                left_action_items: [["arrow-left", lambda x: app.go_to_menu()]]
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "20dp"
                MDBoxLayout:
                    adaptive_height: True
                    MDLabel:
                        text: "Тёмная тема"
                    MDSwitch:
                        id: theme_switch
                        active: app.theme_cls.theme_style == "Dark"
                        on_active: app.toggle_theme(self.active)
                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    spacing: "10dp"
                    MDLabel:
                        text: "Администратор"
                        font_style: "Subtitle1"
                    MDRaisedButton:
                        text: "Выйти из админ-режима" if app.admin_mode else "Войти как администратор"
                        on_release: app.admin_logout() if app.admin_mode else app.show_admin_login()

                MDSeparator:
                    height: "2dp"

                MDLabel:
                    text: "Данные лабораторных"
                    font_style: "Subtitle1"
                    halign: "center"
                MDRaisedButton:
                    text: "Экспорт данных"
                    pos_hint: {"center_x": .5}
                    on_release: app.export_data()
                MDRaisedButton:
                    text: "Импорт из файла"
                    pos_hint: {"center_x": .5}
                    on_release: app.import_from_file()
                MDRaisedButton:
                    text: "Импорт по ссылке"
                    pos_hint: {"center_x": .5}
                    on_release: app.show_import_url_dialog()

    MDScreen:
        name: "physics_list"
        MDBoxLayout:
            orientation: "vertical"
            MDTopAppBar:
                title: "Физика"
                left_action_items: [["arrow-left", lambda x: app.go_to_menu()]]
            ScrollView:
                MDList:
                    id: physics_container
            MDFloatingActionButton:
                icon: "plus"
                pos_hint: {"center_x": .9, "center_y": .1}
                disabled: not app.admin_mode
                on_release: app.go_to_add_lab()

    MDScreen:
        name: "chemistry_list"
        MDBoxLayout:
            orientation: "vertical"
            MDTopAppBar:
                title: "Химия"
                left_action_items: [["arrow-left", lambda x: app.go_to_menu()]]
            ScrollView:
                MDList:
                    id: chemistry_container
            MDFloatingActionButton:
                icon: "plus"
                pos_hint: {"center_x": .9, "center_y": .1}
                disabled: not app.admin_mode
                on_release: app.go_to_add_lab()

    MDScreen:
        name: "add_lab"
        MDBoxLayout:
            orientation: "vertical"
            MDTopAppBar:
                title: "Новая лабораторная"
                left_action_items: [["close", lambda x: app.go_back_to_list()]]
            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "20dp"
                    spacing: "10dp"
                    adaptive_height: True
                    MDTextField:
                        id: new_name
                        hint_text: "Название темы"
                        required: True
                    MDTextField:
                        id: new_video1
                        hint_text: "Ссылка на видео 1 (обязательно)"
                        helper_text: "Любая ссылка: YouTube, VK, Яндекс.Диск и т.д."
                        helper_text_mode: "on_focus"
                        required: True
                    MDTextField:
                        id: new_video2
                        hint_text: "Ссылка на видео 2 (необязательно)"
                        helper_text: "Любая ссылка: YouTube, VK, Яндекс.Диск и т.д."
                    MDTextField:
                        id: new_tools
                        hint_text: "Инструменты"
                        multiline: True
                    MDTextField:
                        id: new_questions
                        hint_text: "Вопросы"
                        multiline: True
                    MDRaisedButton:
                        text: "СОХРАНИТЬ"
                        pos_hint: {"center_x": .5}
                        on_release: app.add_new_lab()

    MDScreen:
        name: "lab_details"
        MDBoxLayout:
            orientation: "vertical"
            MDTopAppBar:
                id: details_title
                left_action_items: [["arrow-left", lambda x: app.go_back_to_list()]]
            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "10dp"
                    spacing: "15dp"
                    adaptive_height: True

                    MDLabel:
                        text: "Видео материалы:"
                        font_style: "H6"

                    MDRaisedButton:
                        id: btn_video1
                        text: "Смотреть видео 1"
                        size_hint_x: 0.8
                        pos_hint: {"center_x": .5}
                        on_release: app.open_video_in_browser(app.labs_data.get(details_title.title, {}).get('v1', ''))
                        disabled: not app.labs_data.get(details_title.title, {}).get('v1', '')
                    MDRaisedButton:
                        id: btn_video2
                        text: "Смотреть видео 2"
                        size_hint_x: 0.8
                        pos_hint: {"center_x": .5}
                        on_release: app.open_video_in_browser(app.labs_data.get(details_title.title, {}).get('v2', ''))
                        disabled: not app.labs_data.get(details_title.title, {}).get('v2', '')

                    MDSeparator:

                    MDLabel:
                        text: "Необходимые инструменты:"
                        font_style: "Subtitle1"
                        theme_text_color: "Primary"
                    MDLabel:
                        id: lab_tools
                        adaptive_height: True

                    MDSeparator:

                    MDLabel:
                        text: "Контрольные вопросы:"
                        font_style: "Subtitle1"
                        theme_text_color: "Primary"
                    MDLabel:
                        id: lab_qs
                        adaptive_height: True
'''


class LabApp(MDApp):
    current_subject = StringProperty("physics")
    labs_data = DictProperty({})  # key: lab_name, value: dict(v1, v2, tools, qs, subject)
    last_opened_subject = StringProperty("")
    last_opened_lab = StringProperty("")
    admin_mode = BooleanProperty(False)

    def build(self):
        self.theme_cls.primary_palette = "Indigo"

        # --- Диалог входа администратора (исправлено) ---
        self.admin_dialog = MDDialog(
            title="Вход администратора",
            type="custom",
            content_cls=MDTextField(
                hint_text="Пароль",
                password=True,
                id="admin_pass"
            ),
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    on_release=lambda x: self.admin_dialog.dismiss()
                ),
                MDFlatButton(
                    text="Войти",
                    on_release=lambda x: self.admin_login()
                ),
            ],
        )

        # --- Диалог для импорта по URL ---
        self.url_dialog = MDDialog(
            title="Импорт по ссылке",
            type="custom",
            content_cls=MDTextField(
                hint_text="Введите URL JSON-файла"
            ),
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    on_release=lambda x: self.url_dialog.dismiss()
                ),
                MDFlatButton(
                    text="Загрузить",
                    on_release=lambda x: self.start_url_import()
                ),
            ],
        )

        # --- Файловый менеджер ---
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager_callback,
            select_path=self.select_path_callback,
        )
        self.file_action = None  # "export" или "import_file"

        root = Builder.load_string(KV)
        # После загрузки интерфейса обновляем списки (если данные уже есть)
        Clock.schedule_once(lambda dt: self.refresh_lists())
        return root

    # --- Удобный метод для снекбаров ---
    def show_snackbar(self, text):
        snackbar = MDSnackbar()
        snackbar.text = text
        snackbar.open()

    def go_to_menu(self):
        self.root.current = "menu"

    def toggle_theme(self, value):
        self.theme_cls.theme_style = "Dark" if value else "Light"

    def continue_last_lab(self):
        if self.last_opened_lab and self.last_opened_subject:
            self.current_subject = self.last_opened_subject
            self.open_lab(self.last_opened_lab)

    # --- Админ-доступ (исправлена ошибка) ---
    def show_admin_login(self):
        # Сбрасываем состояние ошибки перед каждым открытием
        self.admin_dialog.content_cls.text = ""
        self.admin_dialog.content_cls.error = False
        self.admin_dialog.content_cls.helper_text = ""
        self.admin_dialog.open()

    def admin_login(self):
        password = self.admin_dialog.content_cls.text
        if password == "admin123":
            self.admin_mode = True
            self.admin_dialog.dismiss()
            self.show_snackbar("Вы вошли как администратор")
        else:
            self.admin_dialog.content_cls.error = True
            self.admin_dialog.content_cls.helper_text = "Неверный пароль"

    def admin_logout(self):
        self.admin_mode = False
        self.show_snackbar("Вы вышли из режима администратора")
        if self.root.current == "add_lab":
            self.go_back_to_list()

    def go_to_add_lab(self):
        if self.admin_mode:
            self.root.current = "add_lab"
        else:
            self.show_snackbar("Требуются права администратора")

    # --- Работа с данными (учёт предмета) ---
    def add_new_lab(self):
        if not self.admin_mode:
            self.show_snackbar("Требуются права администратора")
            return

        name = self.root.ids.new_name.text.strip()
        v1 = self.root.ids.new_video1.text.strip()
        v2 = self.root.ids.new_video2.text.strip()
        tools = self.root.ids.new_tools.text.strip()
        qs = self.root.ids.new_questions.text.strip()

        if not name:
            self.show_snackbar("Введите название лабораторной!")
            return
        if not v1:
            self.show_snackbar("Укажите ссылку на первое видео (обязательно)!")
            return

        # Сохраняем с указанием предмета
        self.labs_data[name] = {
            "v1": v1,
            "v2": v2,
            "tools": tools,
            "qs": qs,
            "subject": self.current_subject,  # <-- ключевое изменение
        }

        self.clear_fields()
        self.go_back_to_list()
        self.refresh_lists()  # обновить оба списка

    def refresh_lists(self):
        """Очищает и заново заполняет списки лабораторных согласно subject."""
        physics_list = self.root.ids.physics_container
        chemistry_list = self.root.ids.chemistry_container
        physics_list.clear_widgets()
        chemistry_list.clear_widgets()

        for name, data in self.labs_data.items():
            subject = data.get("subject", "")
            item = OneLineListItem(text=name)
            item.bind(on_release=lambda x: self.open_lab(x.text))
            if subject == "physics":
                physics_list.add_widget(item)
            elif subject == "chemistry":
                chemistry_list.add_widget(item)

    def open_lab(self, lab_name):
        data = self.labs_data.get(lab_name, {})
        self.root.ids.details_title.title = lab_name
        self.root.ids.lab_tools.text = data.get('tools', '')
        self.root.ids.lab_qs.text = data.get('qs', '')
        self.last_opened_lab = lab_name
        self.last_opened_subject = data.get("subject", self.current_subject)
        self.current_subject = self.last_opened_subject  # синхронизируем
        self.root.current = "lab_details"

    def open_video_in_browser(self, url):
        if url:
            webbrowser.open(url)
        else:
            self.show_snackbar("Ссылка отсутствует!")

    def go_back_to_list(self):
        target = "physics_list" if self.current_subject == "physics" else "chemistry_list"
        self.root.current = target

    def clear_fields(self):
        for f in ["new_name", "new_video1", "new_video2", "new_tools", "new_questions"]:
            self.root.ids[f].text = ""

    # ========== ЭКСПОРТ / ИМПОРТ ==========
    def export_data(self):
        """Экспорт данных в JSON: открываем выбор папки."""
        self.file_action = "export"
        self.file_manager.show(os.path.expanduser("~"))  # начальная директория

    def import_from_file(self):
        """Импорт данных из локального файла: открываем выбор файла."""
        self.file_action = "import_file"
        self.file_manager.show(os.path.expanduser("~"))

    def show_import_url_dialog(self):
        """Показать диалог ввода URL для импорта."""
        self.url_dialog.content_cls.text = ""
        self.url_dialog.open()

    def start_url_import(self):
        """Запускает загрузку JSON по ссылке в фоновом потоке."""
        url = self.url_dialog.content_cls.text.strip()
        if not url:
            self.show_snackbar("Введите ссылку")
            return
        self.url_dialog.dismiss()
        # Выполняем загрузку в отдельном потоке, чтобы не подвисал интерфейс
        threading.Thread(target=self.download_and_import, args=(url,), daemon=True).start()

    def download_and_import(self, url):
        """Фоновая загрузка JSON и импорт."""
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
            # Проверяем, что это словарь с ожидаемой структурой
            if not isinstance(data, dict):
                raise ValueError("Некорректный формат данных")
            # Обновляем UI в главном потоке
            Clock.schedule_once(lambda dt: self.merge_imported_data(data))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_snackbar(f"Ошибка импорта: {e}"))

    def merge_imported_data(self, imported_data):
        """Объединяет импортированные данные с текущими и обновляет списки."""
        for name, info in imported_data.items():
            if isinstance(info, dict) and "v1" in info:
                # Если предмет не указан, оставляем как есть или ставим physics
                if "subject" not in info:
                    info["subject"] = "physics"
                self.labs_data[name] = info
            else:
                self.show_snackbar(f"Пропущена запись '{name}': неверный формат")
        self.refresh_lists()
        self.show_snackbar("Импорт завершён")

    # --- Обработчики файлового менеджера ---
    def exit_manager_callback(self, *args):
        """Выход из менеджера."""
        self.file_action = None
        self.file_manager.close()

    def select_path_callback(self, path):
        """Обработка выбранного пути."""
        if self.file_action == "export":
            self._do_export(path)
        elif self.file_action == "import_file":
            self._do_import_file(path)
        self.file_manager.close()
        self.file_action = None

    def _do_export(self, folder_path):
        """Сохраняет labs_data.json в выбранную папку."""
        file_path = os.path.join(folder_path, "labs_data.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(dict(self.labs_data), f, ensure_ascii=False, indent=2)
            self.show_snackbar(f"Данные сохранены: {file_path}")
        except Exception as e:
            self.show_snackbar(f"Ошибка сохранения: {e}")

    def _do_import_file(self, file_path):
        """Загружает данные из выбранного JSON-файла."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Файл должен содержать объект JSON")
            self.merge_imported_data(data)
        except Exception as e:
            self.show_snackbar(f"Ошибка чтения файла: {e}")


if __name__ == "__main__":
    LabApp().run()

