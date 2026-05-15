from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.list import OneLineListItem
from kivy.properties import StringProperty, DictProperty, BooleanProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
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
            MDRaisedButton:
                text: "Методички"
                size_hint_x: 0.8
                pos_hint: {"center_x": .5}
                on_release: app.go_to_manuals()
            ScrollView:
                MDList:
                    id: physics_container
            MDFloatingActionButton:
                icon: "plus"
                pos_hint: {"center_x": .9, "center_y": .1}
                opacity: 1 if app.admin_mode else 0
                disabled: not app.admin_mode
                on_release: app.go_to_add_lab()

    MDScreen:
        name: "chemistry_list"
        MDBoxLayout:
            orientation: "vertical"
            MDTopAppBar:
                title: "Химия"
                left_action_items: [["arrow-left", lambda x: app.go_to_menu()]]
            MDRaisedButton:
                text: "Методички"
                size_hint_x: 0.8
                pos_hint: {"center_x": .5}
                on_release: app.go_to_manuals()
            ScrollView:
                MDList:
                    id: chemistry_container
            MDFloatingActionButton:
                icon: "plus"
                pos_hint: {"center_x": .9, "center_y": .1}
                opacity: 1 if app.admin_mode else 0
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
                    spacing: "15dp"
                    adaptive_height: True
                    MDTextField:
                        id: new_name
                        hint_text: "Название темы"
                        required: True
                    MDTextField:
                        id: new_goal
                        hint_text: "Цель работы"
                        required: False
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
                    spacing: "12dp"
                    adaptive_height: True

                    MDLabel:
                        text: "Цель: " + app.detail_goal
                        adaptive_height: True
                        size_hint_y: None
                        height: self.texture_size[1] if app.detail_goal else 0
                        opacity: 1 if app.detail_goal else 0
                        disabled: not bool(app.detail_goal)
                        theme_text_color: "Primary"
                        font_style: "Subtitle1"
                        halign: "center"

                    MDSeparator:

                    MDLabel:
                        text: "Видео материалы:"
                        font_style: "H6"
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDRaisedButton:
                        text: "Смотреть видео 1"
                        size_hint_x: 0.8
                        size_hint_y: None
                        height: "48dp"
                        pos_hint: {"center_x": .5}
                        on_release: app.open_video_in_browser(app.detail_video1)
                        disabled: not bool(app.detail_video1)

                    MDRaisedButton:
                        text: "Смотреть видео 2"
                        size_hint_x: 0.8
                        size_hint_y: None
                        height: "48dp"
                        pos_hint: {"center_x": .5}
                        on_release: app.open_video_in_browser(app.detail_video2)
                        disabled: not bool(app.detail_video2)

                    MDSeparator:
                        opacity: 1 if app.detail_tools else 0
                        size_hint_y: None
                        height: "2dp" if app.detail_tools else 0
                    MDLabel:
                        text: "Необходимые инструменты:"
                        font_style: "Subtitle1"
                        theme_text_color: "Primary"
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1] if app.detail_tools else 0
                        opacity: 1 if app.detail_tools else 0
                        disabled: not bool(app.detail_tools)
                    MDLabel:
                        text: app.detail_tools
                        adaptive_height: True
                        size_hint_y: None
                        height: self.texture_size[1] if app.detail_tools else 0
                        opacity: 1 if app.detail_tools else 0
                        disabled: not bool(app.detail_tools)

                    MDSeparator:
                        opacity: 1 if app.detail_questions else 0
                        size_hint_y: None
                        height: "2dp" if app.detail_questions else 0
                    MDLabel:
                        text: "Контрольные вопросы:"
                        font_style: "Subtitle1"
                        theme_text_color: "Primary"
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1] if app.detail_questions else 0
                        opacity: 1 if app.detail_questions else 0
                        disabled: not bool(app.detail_questions)
                    MDLabel:
                        text: app.detail_questions
                        adaptive_height: True
                        size_hint_y: None
                        height: self.texture_size[1] if app.detail_questions else 0
                        opacity: 1 if app.detail_questions else 0
                        disabled: not bool(app.detail_questions)

    MDScreen:
        name: "manuals"
        MDBoxLayout:
            orientation: "vertical"
            MDTopAppBar:
                title: "Методички - " + ("Физика" if app.current_subject == "physics" else "Химия")
                left_action_items: [["arrow-left", lambda x: app.go_back_to_list()]]
            ScrollView:
                MDList:
                    id: manuals_container
            MDFloatingActionButton:
                icon: "plus"
                pos_hint: {"center_x": .9, "center_y": .1}
                opacity: 1 if app.admin_mode else 0
                disabled: not app.admin_mode
                on_release: app.show_add_manual_dialog()
'''


class LabApp(MDApp):
    current_subject = StringProperty("physics")
    labs_data = DictProperty({})
    manuals_data = DictProperty({})
    last_opened_subject = StringProperty("")
    last_opened_lab = StringProperty("")
    admin_mode = BooleanProperty(False)

    detail_goal = StringProperty("")
    detail_tools = StringProperty("")
    detail_questions = StringProperty("")
    detail_video1 = StringProperty("")
    detail_video2 = StringProperty("")

    def build(self):
        Window.minimum_width = 800
        Window.minimum_height = 600
        self.theme_cls.primary_palette = "Indigo"

        self.manuals_data = {"physics": [], "chemistry": []}

        self.admin_dialog = MDDialog(
            title="Вход администратора",
            type="custom",
            content_cls=MDTextField(
                hint_text="Пароль",
                password=True,
                id="admin_pass"
            ),
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.admin_dialog.dismiss()),
                MDFlatButton(text="Войти", on_release=lambda x: self.admin_login()),
            ],
        )
        self.admin_dialog.content_cls.bind(on_text_validate=lambda instance: self.admin_login())

        self.url_dialog = MDDialog(
            title="Импорт по ссылке",
            type="custom",
            content_cls=MDTextField(hint_text="Введите URL JSON-файла"),
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.url_dialog.dismiss()),
                MDFlatButton(text="Загрузить", on_release=lambda x: self.start_url_import()),
            ],
        )

        manual_content = MDBoxLayout(orientation="vertical", spacing="10dp", adaptive_height=True)
        self.manual_title_field = MDTextField(hint_text="Название")
        self.manual_url_field = MDTextField(hint_text="Ссылка")
        manual_content.add_widget(self.manual_title_field)
        manual_content.add_widget(self.manual_url_field)

        self.manual_dialog = MDDialog(
            title="Добавить методичку",
            type="custom",
            content_cls=manual_content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.manual_dialog.dismiss()),
                MDFlatButton(text="Сохранить", on_release=lambda x: self.save_manual()),
            ],
        )
        self.editing_manual_index = None

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager_callback,
            select_path=self.select_path_callback,
        )
        self.file_action = None

        root = Builder.load_string(KV)
        Clock.schedule_once(lambda dt: self.refresh_lists())
        Clock.schedule_once(lambda dt: threading.Thread(target=self.startup_import, daemon=True).start(), 0.5)
        return root

    # Административные методы
    def go_to_menu(self):
        self.root.current = "menu"

    def toggle_theme(self, value):
        self.theme_cls.theme_style = "Dark" if value else "Light"

    def continue_last_lab(self):
        if self.last_opened_lab and self.last_opened_subject:
            self.current_subject = self.last_opened_subject
            self.open_lab(self.last_opened_lab)

    def show_admin_login(self):
        self.admin_dialog.content_cls.text = ""
        self.admin_dialog.content_cls.error = False
        self.admin_dialog.content_cls.helper_text = ""
        self.admin_dialog.open()

    def admin_login(self):
        password = self.admin_dialog.content_cls.text
        if password == "admin123":
            self.admin_mode = True
            self.admin_dialog.dismiss()
        else:
            self.admin_dialog.content_cls.error = True
            self.admin_dialog.content_cls.helper_text = "Неверный пароль"

    def admin_logout(self):
        self.admin_mode = False
        if self.root.current == "add_lab":
            self.go_back_to_list()

    def go_to_add_lab(self):
        if self.admin_mode:
            self.root.current = "add_lab"

    # Работа с лабораторными
    def add_new_lab(self):
        if not self.admin_mode:
            return

        name = self.root.ids.new_name.text.strip()
        goal = self.root.ids.new_goal.text.strip()
        v1 = self.root.ids.new_video1.text.strip()
        v2 = self.root.ids.new_video2.text.strip()
        tools = self.root.ids.new_tools.text.strip()
        qs = self.root.ids.new_questions.text.strip()

        if not name or not v1:
            return

        self.labs_data[name] = {
            "v1": v1,
            "v2": v2,
            "tools": tools,
            "qs": qs,
            "goal": goal,
            "subject": self.current_subject,
        }

        self.clear_fields()
        self.go_back_to_list()
        self.refresh_lists()

    def refresh_lists(self):
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

        self.detail_goal = data.get('goal', '')
        self.detail_tools = data.get('tools', '')
        self.detail_questions = data.get('qs', '')
        self.detail_video1 = data.get('v1', '')
        self.detail_video2 = data.get('v2', '')

        self.last_opened_lab = lab_name
        self.last_opened_subject = data.get("subject", self.current_subject)
        self.current_subject = self.last_opened_subject
        self.root.current = "lab_details"

    def open_video_in_browser(self, url):
        if url:
            webbrowser.open(url)

    def go_back_to_list(self):
        target = "physics_list" if self.current_subject == "physics" else "chemistry_list"
        self.root.current = target

    def clear_fields(self):
        for f in ["new_name", "new_goal", "new_video1", "new_video2", "new_tools", "new_questions"]:
            self.root.ids[f].text = ""

    # Методички
    def go_to_manuals(self):
        self.refresh_manuals_list()
        self.root.current = "manuals"

    def refresh_manuals_list(self):
        container = self.root.ids.manuals_container
        container.clear_widgets()
        manuals = self.manuals_data.get(self.current_subject, [])
        for i, m in enumerate(manuals):
            box = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing="10dp",
                padding="5dp"
            )
            btn = MDRaisedButton(
                text=m["title"],
                size_hint_x=0.7,
                on_release=lambda x, url=m["url"]: self.open_video_in_browser(url)
            )
            box.add_widget(btn)
            if self.admin_mode:
                edit_btn = MDIconButton(
                    icon="pencil",
                    pos_hint={"center_y": .5},
                    on_release=lambda x, idx=i: self.edit_manual(idx)
                )
                delete_btn = MDIconButton(
                    icon="delete",
                    pos_hint={"center_y": .5},
                    on_release=lambda x, idx=i: self.delete_manual(idx)
                )
                box.add_widget(edit_btn)
                box.add_widget(delete_btn)
            container.add_widget(box)

    def show_add_manual_dialog(self):
        self.manual_title_field.text = ""
        self.manual_url_field.text = ""
        self.manual_dialog.title = "Добавить методичку"
        self.manual_dialog.buttons[1].text = "Сохранить"
        self.editing_manual_index = None
        self.manual_dialog.open()

    def edit_manual(self, index):
        manuals = self.manuals_data.get(self.current_subject, [])
        if 0 <= index < len(manuals):
            m = manuals[index]
            self.manual_title_field.text = m["title"]
            self.manual_url_field.text = m["url"]
            self.manual_dialog.title = "Редактировать методичку"
            self.manual_dialog.buttons[1].text = "Обновить"
            self.editing_manual_index = index
            self.manual_dialog.open()

    def save_manual(self):
        title = self.manual_title_field.text.strip()
        url = self.manual_url_field.text.strip()
        if not title or not url:
            return

        subject = self.current_subject
        if subject not in self.manuals_data:
            self.manuals_data[subject] = []

        if self.editing_manual_index is not None:
            idx = self.editing_manual_index
            if 0 <= idx < len(self.manuals_data[subject]):
                self.manuals_data[subject][idx] = {"title": title, "url": url}
        else:
            self.manuals_data[subject].append({"title": title, "url": url})

        self.manual_dialog.dismiss()
        self.refresh_manuals_list()

    def delete_manual(self, index):
        subject = self.current_subject
        if subject in self.manuals_data and 0 <= index < len(self.manuals_data[subject]):
            del self.manuals_data[subject][index]
            self.refresh_manuals_list()

    # Экспорт/импорт
    def export_data(self):
        self.file_action = "export"
        self.file_manager.show(os.path.expanduser("~"))

    def import_from_file(self):
        self.file_action = "import_file"
        self.file_manager.show(os.path.expanduser("~"))

    def show_import_url_dialog(self):
        self.url_dialog.content_cls.text = ""
        self.url_dialog.open()

    def start_url_import(self):
        url = self.url_dialog.content_cls.text.strip()
        if not url:
            return
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        self.url_dialog.dismiss()
        threading.Thread(target=self.download_and_import, args=(url,), daemon=True).start()

    def download_and_import(self, url):
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=15) as response:
                raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
            Clock.schedule_once(lambda dt, d=data: self.process_imported_data(d))
        except Exception:
            pass  # silently ignore errors

    def process_imported_data(self, data):
        if isinstance(data, dict):
            if "labs" in data:
                self.merge_imported_labs(data["labs"])
            if "manuals" in data:
                self.manuals_data = data["manuals"]
            if "labs" not in data and "manuals" not in data:
                self.merge_imported_labs(data)
        self.refresh_lists()
        self.refresh_manuals_list()

    def merge_imported_labs(self, labs):
        for name, info in labs.items():
            if isinstance(info, dict) and "v1" in info:
                if "subject" not in info:
                    info["subject"] = "physics"
                self.labs_data[name] = info

    def startup_import(self):
        url = "https://github.com/vinpap2008S/FizoksProgect/blob/master/labs_data.json"
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=15) as response:
                raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
            if isinstance(data, dict):
                Clock.schedule_once(lambda dt, d=data: self.process_imported_data(d))
        except Exception:
            pass

    def exit_manager_callback(self, *args):
        self.file_action = None
        self.file_manager.close()

    def select_path_callback(self, path):
        if self.file_action == "export":
            self._do_export(path)
        elif self.file_action == "import_file":
            self._do_import_file(path)
        self.file_manager.close()
        self.file_action = None

    def _do_export(self, folder_path):
        file_path = os.path.join(folder_path, "labs_data.json")
        try:
            export_data = {
                "labs": dict(self.labs_data),
                "manuals": dict(self.manuals_data)
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _do_import_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.process_imported_data(data)
        except Exception:
            pass


if __name__ == "__main__":
    LabApp().run()