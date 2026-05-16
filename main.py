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
from kivy.metrics import dp
import webbrowser
import json
import os
import threading
import re
from urllib.request import urlopen, Request

# Глобальная переменная для включения/отключения режима администратора
ADMIN_MODE = True  # Измените на False, чтобы отключить админ-режим

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
            id: status_box
            adaptive_height: True
            size_hint_y: None
            height: self.minimum_height if app.status_message else 0
            opacity: 1 if app.status_message else 0
            md_bg_color: app.theme_cls.primary_color
            padding: "8dp"
            MDLabel:
                text: app.status_message
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                halign: "center"
                font_style: "Caption"

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
                icon: "history"
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
                    icon: "atom"
                    size_hint: (0.8, None)
                    pos_hint: {"center_x": .5}
                    on_release: app.go_to_subject("physics")
                MDRaisedButton:
                    text: "ХИМИЯ"
                    icon: "flask-variant"
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
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "25dp"
                adaptive_height: True

                MDBoxLayout:
                    adaptive_height: True
                    spacing: "10dp"
                    MDIcon:
                        icon: "theme-light-dark"
                        size_hint: None, None
                        size: "30dp", "30dp"
                        pos_hint: {"center_y": .5}
                    MDLabel:
                        text: "Тёмная тема"
                        font_style: "Subtitle1"
                    MDSwitch:
                        id: theme_switch
                        active: app.theme_cls.theme_style == "Dark"
                        on_active: app.toggle_theme(self.active)

                MDSeparator:

                MDLabel:
                    text: "О приложении"
                    font_style: "H6"
                    halign: "center"

                MDRaisedButton:
                    text: "GitHub проекта"
                    icon: "github"
                    size_hint_x: 0.8
                    pos_hint: {"center_x": .5}
                    on_release: app.open_url("https://github.com/vinpap2008S/FizoksProgect")

                MDRaisedButton:
                    text: "Автор: vinpap2008S"
                    icon: "account"
                    size_hint_x: 0.8
                    pos_hint: {"center_x": .5}
                    on_release: app.open_url("https://github.com/vinpap2008S")

                MDRaisedButton:
                    text: "Проверить обновления"
                    icon: "update"
                    size_hint_x: 0.8
                    pos_hint: {"center_x": .5}
                    on_release: app.open_url("https://github.com/vinpap2008S/FizoksProgect/releases")

                MDRaisedButton:
                    text: "Сообщить об ошибке"
                    icon: "bug"
                    size_hint_x: 0.8
                    pos_hint: {"center_x": .5}
                    on_release: app.open_url("https://github.com/vinpap2008S/FizoksProgect/issues")


<SubjectListScreen>:
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Физика" if root.subject == "physics" else "Химия"
            left_action_items: [["arrow-left", lambda x: app.go_to_menu()]]
        MDRaisedButton:
            text: "Методички"
            icon: "book-open-page-variant"
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
                    helper_text: "Прямая ссылка на видеофайл или страница видео"
                    helper_text_mode: "on_focus"
                    required: True
                MDTextField:
                    id: new_video2
                    hint_text: "Ссылка на видео 2"
                    helper_text: "Прямая ссылка на видеофайл или страница видео"
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
                    icon: "content-save"
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

                # Разделитель перед видео 1
                MDSeparator:
                    id: sep_before_v1
                    size_hint_y: None
                    height: "2dp"
                    opacity: 1

                # Блок видео 1
                MDBoxLayout:
                    id: video1_box
                    orientation: "vertical"
                    adaptive_height: True
                    size_hint_y: None
                    height: self.minimum_height if app.current_lab_v1 else 0
                    opacity: 1 if app.current_lab_v1 else 0
                    disabled: not bool(app.current_lab_v1)
                    spacing: "5dp"

                    MDLabel:
                        id: video1_label
                        text: "Видео 1:"
                        font_style: "H6"
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1] if app.current_lab_v1 else 0
                    BoxLayout:
                        id: video_container_1
                        size_hint_y: None
                        height: "250dp" if app.current_lab_v1 else 0

                # Разделитель перед видео 2
                MDSeparator:
                    id: sep_before_v2
                    size_hint_y: None
                    height: "2dp"
                    opacity: 1

                # Блок видео 2
                MDBoxLayout:
                    id: video2_box
                    orientation: "vertical"
                    adaptive_height: True
                    size_hint_y: None
                    height: self.minimum_height if app.current_lab_v2 else 0
                    opacity: 1 if app.current_lab_v2 else 0
                    disabled: not bool(app.current_lab_v2)
                    spacing: "5dp"

                    MDLabel:
                        id: video2_label
                        text: "Видео 2:"
                        font_style: "H6"
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1] if app.current_lab_v2 else 0
                    BoxLayout:
                        id: video_container_2
                        size_hint_y: None
                        height: "250dp" if app.current_lab_v2 else 0

                # Разделитель после видео (перед инструментами)
                MDSeparator:
                    id: sep_after_video
                    size_hint_y: None
                    height: "2dp"
                    opacity: 1

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_player = None
        self._link_btn_v1 = None
        self._link_btn_v2 = None

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        self.ids.lab_goal_label.text = "Цель: " + app.current_lab_goal if app.current_lab_goal else ""
        self.ids.lab_tools_label.text = app.current_lab_tools
        self.ids.lab_questions_label.text = app.current_lab_questions
        self.ids.details_title.title = app.current_lab_name

        self._manage_visibility(app)

        # Настройка видео с передачей video_box
        self._setup_video(self.ids.video_container_1, app.current_lab_v1, "Видео 1", self.ids.video1_box, 1)
        self._setup_video(self.ids.video_container_2, app.current_lab_v2, "Видео 2", self.ids.video2_box, 2)

    def _manage_visibility(self, app):
        # Видимость блоков управляется в KV через свойства app
        pass

    def _setup_video(self, container, source, label_text, video_box, num):
        container.clear_widgets()
        # Удаляем старую кнопку-ссылку из video_box (если была)
        if num == 1 and self._link_btn_v1:
            video_box.remove_widget(self._link_btn_v1)
            self._link_btn_v1 = None
        elif num == 2 and self._link_btn_v2:
            video_box.remove_widget(self._link_btn_v2)
            self._link_btn_v2 = None

        if not source:
            return
        if self._is_youtube(source):
            self._show_browser_button(container, source, label_text, video_box, num)
            return
        if "drive.google.com" in source:
            direct_url = self._process_url(source)
            self._try_stream_video(container, direct_url, label_text, video_box, num, original_url=source)
            return
        self._show_browser_button(container, source, label_text, video_box, num)

    def _process_url(self, url):
        if "pixeldrain.com/u/" in url:
            url = url.replace("pixeldrain.com/u/", "pixeldrain.com/api/file/")
        drive_match = re.search(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)", url)
        if drive_match:
            file_id = drive_match.group(1)
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return url

    def _try_stream_video(self, container, url, label_text, video_box, num, original_url):
        """Добавляет плеер в container, а кнопку-ссылку — в video_box."""
        container.clear_widgets()
        player = VideoPlayer(
            source=url,
            state='play',
            options={'eos': 'loop'},
            size_hint=(1, 1)
        )
        container.add_widget(player)
        self._current_player = player

        # Создаём кнопку-ссылку и добавляем в video_box (ниже контейнера)
        btn = MDRaisedButton(
            text="Открыть ссылку",
            icon="open-in-new",
            size_hint=(0.8, None),
            height="40dp",
            pos_hint={"center_x": .5},
            on_release=lambda x, u=original_url: webbrowser.open(u)
        )
        video_box.add_widget(btn)
        if num == 1:
            self._link_btn_v1 = btn
        else:
            self._link_btn_v2 = btn

        # Проверка через 3 секунды
        Clock.schedule_once(lambda dt: self._check_player(container, url, label_text, video_box, num, original_url), 3)

    def _check_player(self, container, url, label_text, video_box, num, original_url):
        """Если плеер не запустился, заменяем на кнопку открытия в браузере и удаляем кнопку-ссылку."""
        if self._current_player and (self._current_player.state != 'play' or
                                      (self._current_player.duration is not None and self._current_player.duration <= 0)):
            self._current_player.state = 'stop'
            self._show_browser_button(container, original_url, label_text, video_box, num)
            self._current_player = None

    def _show_browser_button(self, container, url, label_text, video_box, num):
        """Заменяет содержимое контейнера на кнопку-замену и удаляет кнопку-ссылку из video_box."""
        container.clear_widgets()
        # Убираем кнопку-ссылку, если она была
        if num == 1 and self._link_btn_v1:
            video_box.remove_widget(self._link_btn_v1)
            self._link_btn_v1 = None
        elif num == 2 and self._link_btn_v2:
            video_box.remove_widget(self._link_btn_v2)
            self._link_btn_v2 = None

        btn = MDRaisedButton(
            text=f"Открыть {label_text} в браузере",
            icon="open-in-new",
            size_hint=(0.8, None),
            height="48dp",
            pos_hint={"center_x": .5},
            on_release=lambda x: webbrowser.open(url)
        )
        container.add_widget(btn)

    def _is_youtube(self, url):
        return "youtube.com" in url or "youtu.be" in url

    def on_pre_leave(self, *args):
        if hasattr(self, '_current_player') and self._current_player:
            self._current_player.state = 'stop'
        # Очищаем контейнеры и удаляем кнопки-ссылки
        self.ids.video_container_1.clear_widgets()
        self.ids.video_container_2.clear_widgets()
        if self._link_btn_v1 and self._link_btn_v1.parent:
            self._link_btn_v1.parent.remove_widget(self._link_btn_v1)
        if self._link_btn_v2 and self._link_btn_v2.parent:
            self._link_btn_v2.parent.remove_widget(self._link_btn_v2)
        self._link_btn_v1 = None
        self._link_btn_v2 = None


class ManualsScreen(MDScreen):
    pass


# ===================== ГЛАВНОЕ ПРИЛОЖЕНИЕ =====================
class LabApp(MDApp):
    current_subject = StringProperty("physics")
    labs_data = DictProperty({})
    manuals_data = DictProperty({})
    last_opened_subject = StringProperty("")
    last_opened_lab = StringProperty("")
    admin_mode = BooleanProperty(ADMIN_MODE)
    video_user_agent = StringProperty("Mozilla/5.0")
    status_message = StringProperty("")

    current_lab_name = StringProperty("")
    current_lab_goal = StringProperty("")
    current_lab_tools = StringProperty("")
    current_lab_questions = StringProperty("")
    current_lab_v1 = StringProperty("")
    current_lab_v2 = StringProperty("")

    def build(self):
        Window.minimum_width = 320
        Window.minimum_height = 480
        self.theme_cls.primary_palette = "Indigo"

        self.manuals_data = {"physics": [], "chemistry": []}
        self.local_data_path = os.path.join(self.user_data_dir, 'labs_data.json')

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
                MDFlatButton(text="Сохранить", icon="content-save", on_release=lambda x: self.save_manual()),
            ],
        )
        self.editing_manual_index = None

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager_callback,
            select_path=self.select_path_callback,
        )
        self.file_action = None

        self.retry_attempt = 0
        self.max_retries = 5
        self.retry_timer = None

        root = Builder.load_string(KV)
        Clock.schedule_once(lambda dt: self.refresh_lists())
        Clock.schedule_once(lambda dt: self.try_import_with_retry(), 0.5)
        return root

    # ---------- Навигация ----------
    def go_to_menu(self):
        self.root.current = "menu"

    def go_to_subject(self, subj):
        self.current_subject = subj
        self.root.current = f"{subj}_list"

    def go_to_add_lab(self):
        if self.admin_mode:
            self.root.current = "add_lab"

    def go_back_to_list(self):
        self.root.current = f"{self.current_subject}_list"

    def toggle_theme(self, value):
        self.theme_cls.theme_style = "Dark" if value else "Light"

    def open_url(self, url):
        webbrowser.open(url)

    # ---------- Лабораторные ----------
    def add_new_lab(self):
        if not self.admin_mode:
            return
        screen = self.root.get_screen("add_lab")
        name = screen.ids.new_name.text.strip()
        goal = screen.ids.new_goal.text.strip()
        v1 = screen.ids.new_video1.text.strip()
        v2 = screen.ids.new_video2.text.strip()
        tools = screen.ids.new_tools.text.strip()
        qs = screen.ids.new_questions.text.strip()
        if not name or not v1:
            return
        self.labs_data[name] = {
            "v1": v1, "v2": v2,
            "tools": tools, "qs": qs,
            "goal": goal, "subject": self.current_subject,
        }
        self.clear_fields()
        self.go_back_to_list()
        self.refresh_lists()

    def refresh_lists(self):
        for subj in ("physics", "chemistry"):
            screen = self.root.get_screen(f"{subj}_list")
            cont = screen.ids.container
            cont.clear_widgets()
            sorted_labs = sorted(
                [item for item in self.labs_data.items() if item[1].get("subject") == subj],
                key=lambda x: x[0].lower()
            )
            for name, data in sorted_labs:
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

    # ---------- Методички ----------
    def refresh_manuals_list(self):
        screen = self.root.get_screen("manuals")
        cont = screen.ids.manuals_container
        cont.clear_widgets()
        manuals = self.manuals_data.get(self.current_subject, [])
        for i, m in enumerate(manuals):
            box = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing="10dp", padding="5dp")
            btn = MDRaisedButton(
                text=m["title"],
                icon="book-open-page-variant",
                size_hint_x=0.7,
                on_release=lambda x, url=m["url"]: webbrowser.open(url)
            )
            box.add_widget(btn)
            if self.admin_mode:
                box.add_widget(MDIconButton(icon="pencil", on_release=lambda x, idx=i: self.edit_manual(idx)))
                box.add_widget(MDIconButton(icon="delete", on_release=lambda x, idx=i: self.delete_manual(idx)))
            cont.add_widget(box)

    def show_add_manual_dialog(self):
        if not self.admin_mode:
            return
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
        if not title or not url:
            return
        subj = self.current_subject
        if subj not in self.manuals_data:
            self.manuals_data[subj] = []
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

    # ---------- Импорт базы данных ----------
    def try_import_with_retry(self, attempt=0):
        self.retry_attempt = attempt
        url = "https://github.com/vinpap2008S/FizoksProgect/blob/master/labs_data.json"
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        def download_and_process():
            try:
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req, timeout=15) as resp:
                    raw = resp.read().decode('utf-8')
                data = json.loads(raw)
                if isinstance(data, dict):
                    try:
                        with open(self.local_data_path, "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                    Clock.schedule_once(lambda dt: self.process_imported_data(data))
                    Clock.schedule_once(lambda dt: self._update_status("Данные успешно загружены"))
                    self.retry_attempt = self.max_retries
                else:
                    raise ValueError("Некорректный формат данных")
            except Exception as e:
                if self.retry_attempt < self.max_retries - 1:
                    self.retry_timer = Clock.schedule_once(
                        lambda dt: self.try_import_with_retry(self.retry_attempt + 1), 60
                    )
                    Clock.schedule_once(lambda dt: self._update_status(f"Ошибка загрузки. Повтор через 1 мин ({self.retry_attempt+2}/{self.max_retries})"))
                else:
                    if os.path.exists(self.local_data_path):
                        try:
                            with open(self.local_data_path, "r", encoding="utf-8") as f:
                                local_data = json.load(f)
                            Clock.schedule_once(lambda dt: self.process_imported_data(local_data))
                            Clock.schedule_once(lambda dt: self._update_status("Используются локальные данные"))
                        except Exception:
                            Clock.schedule_once(lambda dt: self._update_status("Не удалось загрузить базу данных"))
                    else:
                        Clock.schedule_once(lambda dt: self._update_status("Не удалось загрузить базу данных"))
                if self.retry_attempt == 0 and os.path.exists(self.local_data_path):
                    try:
                        with open(self.local_data_path, "r", encoding="utf-8") as f:
                            local_data = json.load(f)
                        Clock.schedule_once(lambda dt: self.process_imported_data(local_data))
                        Clock.schedule_once(lambda dt: self._update_status("Используются локальные данные (обновление не удалось)"))
                    except Exception:
                        pass

        threading.Thread(target=download_and_process, daemon=True).start()

    def _update_status(self, message):
        self.status_message = message
        if "Используются" not in message and "Не удалось" not in message:
            Clock.schedule_once(lambda dt: self._hide_status(), 10)

    def _hide_status(self):
        if "Используются" not in self.status_message and "Не удалось" not in self.status_message:
            self.status_message = ""

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

    def on_stop(self):
        if self.retry_timer:
            self.retry_timer.cancel()

    def exit_manager_callback(self, *args):
        self.file_action = None
        self.file_manager.close()

    def select_path_callback(self, path):
        pass


if __name__ == "__main__":
    LabApp().run()