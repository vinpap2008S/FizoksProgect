from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.videoplayer import VideoPlayer
from kivymd.uix.screen import MDScreen
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

    MenuScreen:
        name: "menu"

    SettingsScreen:
        name: "settings"

    SubjectListScreen:
        name: "physics_list"
        subject: "physics"

    SubjectListScreen:
        name: "chemistry_list"
        subject: "chemistry"

    AddLabScreen:
        name: "add_lab"

    LabDetailsScreen:
        name: "lab_details"

    ManualsScreen:
        name: "manuals"


<MenuScreen>:
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
                on_release: root.continue_last_lab()

        AnchorLayout:
            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                spacing: "20dp"
                MDRaisedButton:
                    text: "ФИЗИКА"
                    size_hint: (0.8, None)
                    pos_hint: {"center_x": .5}
                    on_release: app.go_to_subject("physics")
                MDRaisedButton:
                    text: "ХИМИЯ"
                    size_hint: (0.8, None)
                    pos_hint: {"center_x": .5}
                    on_release: app.go_to_subject("chemistry")

        MDFloatingActionButton:
            icon: "cog"
            pos_hint: {"right": 0.95, "y": 0.05}
            on_release: app.root.current = "settings"


<SettingsScreen>:
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


<SubjectListScreen>:
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Физика" if root.subject == "physics" else "Химия"
            left_action_items: [["arrow-left", lambda x: app.go_to_menu()]]
        MDRaisedButton:
            text: "Методички"
            size_hint_x: 0.8
            pos_hint: {"center_x": .5}
            on_release: root.go_to_manuals()
        ScrollView:
            MDList:
                id: container
        MDFloatingActionButton:
            icon: "plus"
            pos_hint: {"center_x": .9, "center_y": .1}
            opacity: 1 if app.admin_mode else 0
            disabled: not app.admin_mode
            on_release: app.go_to_add_lab()


<AddLabScreen>:
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
                MDTextField:
                    id: new_video1
                    hint_text: "Ссылка на видео 1 (обязательно)"
                    helper_text: "Прямая ссылка на видеофайл"
                    helper_text_mode: "on_focus"
                    required: True
                MDTextField:
                    id: new_video2
                    hint_text: "Ссылка на видео 2"
                    helper_text: "Прямая ссылка на видеофайл"
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


<LabDetailsScreen>:
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

                # Цель
                MDLabel:
                    id: lab_goal_label
                    adaptive_height: True
                    size_hint_y: None
                    height: self.texture_size[1] if self.text else 0
                    opacity: 1 if self.text else 0
                    disabled: not bool(self.text)
                    theme_text_color: "Primary"
                    font_style: "Subtitle1"
                    halign: "center"

                MDSeparator:

                # Видео 1
                MDLabel:
                    text: "Видео 1:"
                    font_style: "H6"
                    bold: True
                BoxLayout:
                    id: video_container_1
                    size_hint_y: None
                    height: "250dp"

                MDSeparator:

                # Видео 2 (скрывается, если нет ссылки)
                MDLabel:
                    id: video2_label
                    text: "Видео 2:"
                    font_style: "H6"
                    bold: True
                    size_hint_y: None
                    height: self.texture_size[1] if app.current_lab_v2 else 0
                    opacity: 1 if app.current_lab_v2 else 0
                    disabled: not bool(app.current_lab_v2)
                BoxLayout:
                    id: video_container_2
                    size_hint_y: None
                    height: "250dp" if app.current_lab_v2 else 0
                    opacity: 1 if app.current_lab_v2 else 0
                    disabled: not bool(app.current_lab_v2)

                MDSeparator:

                # Инструменты
                MDLabel:
                    text: "Необходимые инструменты:"
                    font_style: "Subtitle1"
                    theme_text_color: "Primary"
                    bold: True
                    size_hint_y: None
                    height: self.texture_size[1] if app.current_lab_tools else 0
                    opacity: 1 if app.current_lab_tools else 0
                    disabled: not bool(app.current_lab_tools)
                MDLabel:
                    id: lab_tools_label
                    adaptive_height: True
                    size_hint_y: None
                    height: self.texture_size[1] if self.text else 0
                    opacity: 1 if self.text else 0
                    disabled: not bool(self.text)

                MDSeparator:
                    opacity: 1 if app.current_lab_questions else 0
                    size_hint_y: None
                    height: "2dp" if app.current_lab_questions else 0

                # Вопросы
                MDLabel:
                    text: "Контрольные вопросы:"
                    font_style: "Subtitle1"
                    theme_text_color: "Primary"
                    bold: True
                    size_hint_y: None
                    height: self.texture_size[1] if app.current_lab_questions else 0
                    opacity: 1 if app.current_lab_questions else 0
                    disabled: not bool(app.current_lab_questions)
                MDLabel:
                    id: lab_questions_label
                    adaptive_height: True
                    size_hint_y: None
                    height: self.texture_size[1] if self.text else 0
                    opacity: 1 if self.text else 0
                    disabled: not bool(self.text)


<ManualsScreen>:
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


# ===================== ЭКРАНЫ =====================
class MenuScreen(MDScreen):
    def continue_last_lab(self):
        app = MDApp.get_running_app()
        if app.last_opened_lab and app.last_opened_subject:
            app.current_subject = app.last_opened_subject
            app.open_lab(app.last_opened_lab)


class SettingsScreen(MDScreen):
    pass


class SubjectListScreen(MDScreen):
    subject = StringProperty("physics")

    def go_to_manuals(self):
        app = MDApp.get_running_app()
        app.current_subject = self.subject
        app.root.current = "manuals"
        app.refresh_manuals_list()


class AddLabScreen(MDScreen):
    pass


class LabDetailsScreen(MDScreen):
    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        self.ids.lab_goal_label.text = "Цель: " + app.current_lab_goal if app.current_lab_goal else ""
        self.ids.lab_tools_label.text = app.current_lab_tools
        self.ids.lab_questions_label.text = app.current_lab_questions
        self.ids.details_title.title = app.current_lab_name

        self._setup_video(self.ids.video_container_1, app.current_lab_v1, "Видео 1")
        self._setup_video(self.ids.video_container_2, app.current_lab_v2, "Видео 2")

    def _setup_video(self, container, source, label_text):
        container.clear_widgets()
        if not source:
            return
        # YouTube — открываем в браузере
        if self._is_youtube(source):
            btn = MDRaisedButton(
                text=f"Открыть {label_text} в YouTube",
                size_hint=(0.8, None),
                height="48dp",
                pos_hint={"center_x": .5},
                on_release=lambda x: webbrowser.open(source)
            )
            container.add_widget(btn)
            return

        # Для GitHub blob — автоматически raw, без лишнего кодирования
        url = source
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        player = VideoPlayer(
            source=url,
            state='play',
            options={'eos': 'loop'},
            size_hint=(1, 1)
        )
        container.add_widget(player)
        self._current_player = player

    def _is_youtube(self, url):
        return "youtube.com" in url or "youtu.be" in url

    def on_pre_leave(self, *args):
        if hasattr(self, '_current_player') and self._current_player:
            self._current_player.state = 'stop'
        self.ids.video_container_1.clear_widgets()
        self.ids.video_container_2.clear_widgets()


class ManualsScreen(MDScreen):
    pass


# ===================== ГЛАВНОЕ ПРИЛОЖЕНИЕ =====================
class LabApp(MDApp):
    current_subject = StringProperty("physics")
    labs_data = DictProperty({})
    manuals_data = DictProperty({})
    last_opened_subject = StringProperty("")
    last_opened_lab = StringProperty("")
    admin_mode = BooleanProperty(False)

    current_lab_name = StringProperty("")
    current_lab_goal = StringProperty("")
    current_lab_tools = StringProperty("")
    current_lab_questions = StringProperty("")
    current_lab_v1 = StringProperty("")
    current_lab_v2 = StringProperty("")

    def build(self):
        Window.minimum_width = 800
        Window.minimum_height = 600
        self.theme_cls.primary_palette = "Indigo"

        self.manuals_data = {"physics": [], "chemistry": []}

        self.admin_dialog = MDDialog(
            title="Вход администратора",
            type="custom",
            content_cls=MDTextField(hint_text="Пароль", password=True, id="admin_pass"),
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

    # Навигация
    def go_to_menu(self): self.root.current = "menu"
    def go_to_subject(self, subj):
        self.current_subject = subj
        self.root.current = f"{subj}_list"
    def go_to_add_lab(self): self.root.current = "add_lab"
    def go_back_to_list(self): self.root.current = f"{self.current_subject}_list"
    def toggle_theme(self, v): self.theme_cls.theme_style = "Dark" if v else "Light"

    # Администратор
    def show_admin_login(self):
        self.admin_dialog.content_cls.text = ""
        self.admin_dialog.content_cls.error = False
        self.admin_dialog.content_cls.helper_text = ""
        self.admin_dialog.open()

    def admin_login(self):
        if self.admin_dialog.content_cls.text == "admin123":
            self.admin_mode = True
            self.admin_dialog.dismiss()
        else:
            self.admin_dialog.content_cls.error = True
            self.admin_dialog.content_cls.helper_text = "Неверный пароль"

    def admin_logout(self):
        self.admin_mode = False
        if self.root.current == "add_lab":
            self.go_back_to_list()

    # Лабораторные
    def add_new_lab(self):
        if not self.admin_mode: return
        screen = self.root.get_screen("add_lab")
        name = screen.ids.new_name.text.strip()
        goal = screen.ids.new_goal.text.strip()
        v1 = screen.ids.new_video1.text.strip()
        v2 = screen.ids.new_video2.text.strip()
        tools = screen.ids.new_tools.text.strip()
        qs = screen.ids.new_questions.text.strip()
        if not name or not v1: return
        self.labs_data[name] = {"v1": v1, "v2": v2, "tools": tools, "qs": qs, "goal": goal, "subject": self.current_subject}
        self.clear_fields()
        self.go_back_to_list()
        self.refresh_lists()

    def refresh_lists(self):
        for subj in ("physics", "chemistry"):
            screen = self.root.get_screen(f"{subj}_list")
            cont = screen.ids.container
            cont.clear_widgets()
            for name, data in self.labs_data.items():
                if data.get("subject") == subj:
                    item = OneLineListItem(text=name)
                    item.bind(on_release=lambda x, n=name: self.open_lab(n))
                    cont.add_widget(item)

    def open_lab(self, name):
        data = self.labs_data.get(name, {})
        self.current_lab_name = name
        self.current_lab_goal = data.get('goal', '')
        self.current_lab_tools = data.get('tools', '')
        self.current_lab_questions = data.get('qs', '')
        self.current_lab_v1 = data.get('v1', '')
        self.current_lab_v2 = data.get('v2', '')
        self.last_opened_lab = name
        self.last_opened_subject = data.get("subject", self.current_subject)
        self.current_subject = self.last_opened_subject
        self.root.current = "lab_details"

    def clear_fields(self):
        screen = self.root.get_screen("add_lab")
        for fid in ("new_name", "new_goal", "new_video1", "new_video2", "new_tools", "new_questions"):
            screen.ids[fid].text = ""

    # Методички
    def refresh_manuals_list(self):
        screen = self.root.get_screen("manuals")
        cont = screen.ids.manuals_container
        cont.clear_widgets()
        manuals = self.manuals_data.get(self.current_subject, [])
        for i, m in enumerate(manuals):
            box = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing="10dp", padding="5dp")
            btn = MDRaisedButton(text=m["title"], size_hint_x=0.7, on_release=lambda x, url=m["url"]: webbrowser.open(url))
            box.add_widget(btn)
            if self.admin_mode:
                box.add_widget(MDIconButton(icon="pencil", on_release=lambda x, idx=i: self.edit_manual(idx)))
                box.add_widget(MDIconButton(icon="delete", on_release=lambda x, idx=i: self.delete_manual(idx)))
            cont.add_widget(box)

    def show_add_manual_dialog(self):
        self.manual_title_field.text = self.manual_url_field.text = ""
        self.manual_dialog.title = "Добавить методичку"
        self.manual_dialog.buttons[1].text = "Сохранить"
        self.editing_manual_index = None
        self.manual_dialog.open()

    def edit_manual(self, idx):
        manuals = self.manuals_data.get(self.current_subject, [])
        if 0 <= idx < len(manuals):
            m = manuals[idx]
            self.manual_title_field.text = m["title"]
            self.manual_url_field.text = m["url"]
            self.manual_dialog.title = "Редактировать методичку"
            self.manual_dialog.buttons[1].text = "Обновить"
            self.editing_manual_index = idx
            self.manual_dialog.open()

    def save_manual(self):
        title = self.manual_title_field.text.strip()
        url = self.manual_url_field.text.strip()
        if not title or not url: return
        subj = self.current_subject
        if subj not in self.manuals_data: self.manuals_data[subj] = []
        entry = {"title": title, "url": url}
        if self.editing_manual_index is not None:
            idx = self.editing_manual_index
            if 0 <= idx < len(self.manuals_data[subj]):
                self.manuals_data[subj][idx] = entry
        else:
            self.manuals_data[subj].append(entry)
        self.manual_dialog.dismiss()
        self.refresh_manuals_list()

    def delete_manual(self, idx):
        subj = self.current_subject
        if subj in self.manuals_data and 0 <= idx < len(self.manuals_data[subj]):
            del self.manuals_data[subj][idx]
            self.refresh_manuals_list()

    # Экспорт / импорт
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
        if not url: return
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        self.url_dialog.dismiss()
        threading.Thread(target=self.download_and_import, args=(url,), daemon=True).start()

    def download_and_import(self, url):
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            Clock.schedule_once(lambda dt, d=data: self.process_imported_data(d))
        except Exception: pass

    def process_imported_data(self, data):
        if isinstance(data, dict):
            if "labs" in data: self.merge_imported_labs(data["labs"])
            if "manuals" in data: self.manuals_data = data["manuals"]
            if "labs" not in data and "manuals" not in data: self.merge_imported_labs(data)
        self.refresh_lists()
        self.refresh_manuals_list()

    def merge_imported_labs(self, labs):
        for name, info in labs.items():
            if isinstance(info, dict) and "v1" in info:
                if "subject" not in info: info["subject"] = "physics"
                self.labs_data[name] = info

    def startup_import(self):
        url = "https://github.com/vinpap2008S/FizoksProgect/blob/master/labs_data.json"
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            if isinstance(data, dict):
                Clock.schedule_once(lambda dt, d=data: self.process_imported_data(d))
        except Exception: pass

    def exit_manager_callback(self, *args):
        self.file_action = None
        self.file_manager.close()

    def select_path_callback(self, path):
        if self.file_action == "export": self._do_export(path)
        elif self.file_action == "import_file": self._do_import_file(path)
        self.file_manager.close()
        self.file_action = None

    def _do_export(self, folder):
        path = os.path.join(folder, "labs_data.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"labs": dict(self.labs_data), "manuals": dict(self.manuals_data)}, f, ensure_ascii=False, indent=2)
        except Exception: pass

    def _do_import_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.process_imported_data(data)
        except Exception: pass


if __name__ == "__main__":
    LabApp().run()