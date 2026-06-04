import logging
logging.getLogger('kivy.core.image').setLevel(logging.ERROR)

import shutil  # для экспорта файлов

from kivymd.app import MDApp
from kivy.lang import Builder
import sys
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard  # для копирования в буфер обмена
from kivy.uix.videoplayer import VideoPlayer
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivy.properties import StringProperty, DictProperty, BooleanProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
import webbrowser
import json
import os
import threading
import re
from urllib.request import urlopen, Request

ADMIN_MODE = True

# Путь для хранения данных. Оставьте None, чтобы использовать системную папку приложения.
# Пример ручного задания: CUSTOM_DATA_PATH = r"C:\MyAppData"
CUSTOM_DATA_PATH = None

KV = '''
ScreenManager:
    id: screen_manager

    MenuScreen:
        name: "menu"

    SettingsScreen:
        name: "settings"

    SectionListScreen:
        name: "sections_list"

    SubjectListScreen:
        name: "lab_list"

    AddLabScreen:
        name: "add_lab"

    LabDetailsScreen:
        name: "lab_details"

    VarktLabDetailsScreen:
        name: "varkt_lab_details"

    ManualsScreen:
        name: "manuals"

    ThanksScreen:
        name: "thanks"


<MenuScreen>:
    MDScreen:
        canvas.before:
            Rectangle:
                source: 'C:/Users/vikit/PyCharmMiscProject/back_sky.jpeg'
                size: self.size
                pos: self.pos
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
                size_hint_y: None
                height: "6dp"

            MDBoxLayout:
                id: last_lab_box
                orientation: "vertical"
                adaptive_height: True
                padding: "10dp"
                spacing: "15dp"
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
                        md_bg_color: 0.1, 0.7, 0.4, 1
                        icon: "flask-variant"
                        size_hint: (0.8, None)
                        pos_hint: {"center_x": .5}
                        on_release: app.go_to_subject("chemistry")
                    MDRaisedButton:
                        text: "ВАРКТ"
                        md_bg_color: 0.8, 0.4, 0.2, 1.0
                        icon: "rocket"
                        size_hint: (0.8, None)
                        pos_hint: {"center_x": .5}
                        on_release: app.go_to_subject("varkt")

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
                        text: "Тема приложения"
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
                    text: "Благодарности"
                    icon: "hand-heart"
                    size_hint_x: 0.8
                    pos_hint: {"center_x": .5}
                    on_release: app.go_to_thanks()

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

                # ---------- Кнопка управления данными (только для админа) ----------
                MDRaisedButton:
                    text: "Управление данными"
                    icon: "database"
                    size_hint_x: 0.8
                    pos_hint: {"center_x": .5}
                    opacity: 1 if app.admin_mode else 0
                    disabled: not app.admin_mode
                    on_release: app.show_data_management_dialog()


<SectionListScreen>:
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            id: sections_title
            title: ""
            left_action_items: [["arrow-left", lambda x: app.go_to_menu()]]
            right_action_items: [["plus" if app.admin_mode else "", lambda x: app.show_add_section_dialog()]]
        ScrollView:
            MDList:
                id: sections_container


<SubjectListScreen>:
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            id: lab_list_title
            title: ""
            left_action_items: [["arrow-left", lambda x: app.go_back_to_subject_list()]]
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
            left_action_items: [["close", lambda x: app.go_back_to_lab_list()]]
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
                    id: new_section
                    hint_text: "Раздел"
                    readonly: True
                    on_focus: if self.focus: app.show_section_menu()
                MDTextField:
                    id: new_goal
                    hint_text: "Цель работы"
                MDTextField:
                    id: new_video1
                    hint_text: "Ссылка на видео 1 (обязательно)"
                    helper_text: "Прямая ссылка на видеофайл или страница видео"
                    helper_text_mode: "on_focus"
                MDTextField:
                    id: new_video2
                    hint_text: "Ссылка на видео 2"
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
            left_action_items: [["arrow-left", lambda x: app.go_back_to_lab_list()]]
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "10dp"
                spacing: "12dp"
                adaptive_height: True

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
                    id: sep_before_v1
                    size_hint_y: None
                    height: "2dp"
                    opacity: 1

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

                MDSeparator:
                    id: sep_before_v2
                    size_hint_y: None
                    height: "2dp"
                    opacity: 1

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

                MDSeparator:
                    id: sep_after_video
                    size_hint_y: None
                    height: "2dp"
                    opacity: 1

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


<VarktLabDetailsScreen>:
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            id: varkt_title
            title: "ВАРКТ"
            left_action_items: [["arrow-left", lambda x: app.go_back_to_lab_list()]]
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "15dp"
                spacing: "15dp"
                adaptive_height: True

                MDLabel:
                    text: "Тема:"
                    font_style: "Subtitle1"
                    bold: True
                MDLabel:
                    id: varkt_title_label
                    adaptive_height: True
                    text: app.current_varkt_title

                MDLabel:
                    text: "Полезные материалы:"
                    font_style: "Subtitle1"
                    bold: True
                MDRaisedButton:
                    id: varkt_prep_btn
                    text: "Открыть ссылку"
                    icon: "book-open-variant"
                    size_hint_x: 0.8
                    pos_hint: {"center_x": .5}
                    on_release: app.open_url(app.current_varkt_prep)

                MDLabel:
                    text: "Как пройти:"
                    font_style: "Subtitle1"
                    bold: True
                MDRaisedButton:
                    id: varkt_access_btn
                    text: "Открыть ссылку"
                    icon: "map-marker"
                    size_hint_x: 0.8
                    pos_hint: {"center_x": .5}
                    on_release: app.open_url(app.current_varkt_access)


<ManualsScreen>:
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Методички - " + app.get_subject_name(app.current_subject)
            left_action_items: [["arrow-left", lambda x: app.go_back_to_lab_list()]]
        ScrollView:
            MDList:
                id: manuals_container
        MDFloatingActionButton:
            icon: "plus"
            pos_hint: {"center_x": .9, "center_y": .1}
            opacity: 1 if app.admin_mode else 0
            disabled: not app.admin_mode
            on_release: app.show_add_manual_dialog()


<ThanksScreen>:
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Благодарности"
            left_action_items: [["arrow-left", lambda x: app.go_to_menu()]]
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "40dp"
                adaptive_height: True
                MDLabel:
                    text: "Консультировали по содержанию, предоставили лаборатории и вдохновили на создание проекта"
                    font_style: "H6"
                    bold: True
                    size_hint_y: None
                    height: self.texture_size[1]
                MDLabel:
                    text: "Александр Георгиевич Браун – доцент кафедры 915, кандидат технических наук; Иван Сергеевич Сафронов – доцент кафедры 915, кандидат физико-математических наук"
                    theme_text_color: "Secondary"
                MDSeparator:
                    size_hint_y: None
                    height: "2dp"
                MDLabel:
                    text: "Предоставили материалы по ВАРКТу"
                    font_style: "H6"
                    bold: True
                    size_hint_y: None
                    height: self.texture_size[1]
                MDLabel:
                    text: "Волынец Александр, Гадай Игорь, Гринкевич Софья, Павлов Иван, Пожидаев Виктор"
                    theme_text_color: "Secondary"
                MDSeparator:
                    size_hint_y: None
                    height: "2dp"
                MDLabel:
                    text: "Курировал проект"
                    font_style: "H6"
                    bold: True
                    size_hint_y: None
                    height: self.texture_size[1]
                MDLabel:
                    text: "Виктор Юрьевич Мищенко – старший преподаватель кафедры 103"
                    theme_text_color: "Secondary"
'''


# ========== ЭКРАНЫ ==========
class MenuScreen(MDScreen):
    def continue_last_lab(self):
        app = MDApp.get_running_app()
        if app.last_opened_lab and app.last_opened_subject:
            app.current_subject = app.last_opened_subject
            if app.current_subject == "varkt":
                app.current_section = ""
                app.open_varkt_lab(app.last_opened_lab)
            else:
                app.current_section = app.last_opened_section
                app.open_lab(app.last_opened_lab)


class SettingsScreen(MDScreen):
    pass


class SectionListScreen(MDScreen):
    pass


class SubjectListScreen(MDScreen):
    def go_to_manuals(self):
        app = MDApp.get_running_app()
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
        self._setup_video(self.ids.video_container_1, app.current_lab_v1, "Видео 1", self.ids.video1_box, 1)
        self._setup_video(self.ids.video_container_2, app.current_lab_v2, "Видео 2", self.ids.video2_box, 2)

    def _setup_video(self, container, source, label_text, video_box, num):
        container.clear_widgets()
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
        container.clear_widgets()
        player = VideoPlayer(source=url, state='play', options={'eos': 'loop'}, size_hint=(1, 1))
        container.add_widget(player)
        self._current_player = player
        btn = MDRaisedButton(
            text="Открыть ссылку в браузере", icon="open-in-new", size_hint=(0.8, None), height="40dp",
            pos_hint={"center_x": .5}, on_release=lambda x, u=original_url: self.app.open_url(u)
        )
        video_box.add_widget(btn)
        if num == 1:
            self._link_btn_v1 = btn
        else:
            self._link_btn_v2 = btn

    def _show_browser_button(self, container, url, label_text, video_box, num):
        container.clear_widgets()
        if num == 1 and self._link_btn_v1:
            video_box.remove_widget(self._link_btn_v1)
            self._link_btn_v1 = None
        elif num == 2 and self._link_btn_v2:
            video_box.remove_widget(self._link_btn_v2)
            self._link_btn_v2 = None
        btn = MDRaisedButton(
            text=f"Открыть {label_text} в браузере", icon="open-in-new", size_hint=(0.8, None),
            height="48dp", pos_hint={"center_x": .5}, on_release=lambda x: self.app.open_url(url)
        )
        container.add_widget(btn)

    def _is_youtube(self, url):
        return "youtube.com" in url or "youtu.be" in url

    def on_pre_leave(self, *args):
        if hasattr(self, '_current_player') and self._current_player:
            self._current_player.state = 'stop'
        self.ids.video_container_1.clear_widgets()
        self.ids.video_container_2.clear_widgets()
        if self._link_btn_v1 and self._link_btn_v1.parent:
            self._link_btn_v1.parent.remove_widget(self._link_btn_v1)
        if self._link_btn_v2 and self._link_btn_v2.parent:
            self._link_btn_v2.parent.remove_widget(self._link_btn_v2)
        self._link_btn_v1 = None
        self._link_btn_v2 = None

    @property
    def app(self):
        return MDApp.get_running_app()


class VarktLabDetailsScreen(MDScreen):
    pass


class ManualsScreen(MDScreen):
    pass


class ThanksScreen(MDScreen):
    pass


# ========== ГЛАВНОЕ ПРИЛОЖЕНИЕ ==========
class LabApp(MDApp):
    current_subject = StringProperty("physics")
    current_section = StringProperty("")
    last_opened_subject = StringProperty("")
    last_opened_section = StringProperty("")
    last_opened_lab = StringProperty("")
    admin_mode = BooleanProperty(ADMIN_MODE)
    status_message = StringProperty("")

    # поля для физики/химии
    current_lab_name = StringProperty("")
    current_lab_goal = StringProperty("")
    current_lab_tools = StringProperty("")
    current_lab_questions = StringProperty("")
    current_lab_v1 = StringProperty("")
    current_lab_v2 = StringProperty("")

    # поля для ВАРКТ
    current_varkt_title = StringProperty("")
    current_varkt_prep = StringProperty("")
    current_varkt_access = StringProperty("")

    data = DictProperty({})
    manuals_data = DictProperty({"physics": [], "chemistry": [], "varkt": []})

    def build(self):
        Window.minimum_width = 320
        Window.minimum_height = 480
        self.theme_cls.primary_palette = "Indigo"

        if CUSTOM_DATA_PATH:
            base_dir = CUSTOM_DATA_PATH
        else:
            base_dir = self.user_data_dir
        os.makedirs(base_dir, exist_ok=True)
        self.local_data_path = os.path.join(base_dir, 'labs_data.json')
        self.manuals_data_path = os.path.join(base_dir, 'manuals_data.json')

        self.init_manual_dialog()

        self.file_manager = MDFileManager(exit_manager=self.exit_manager_callback, select_path=self.select_path_callback)
        self.retry_attempt = 0
        self.max_retries = 5
        self.retry_timer = None
        self.section_menu = None

        root = Builder.load_string(KV)
        Clock.schedule_once(lambda dt: self.try_import_with_retry(), 0.5)
        return root

    def init_manual_dialog(self):
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

    # ---------- Навигация ----------
    def go_to_menu(self):
        self.root.current = "menu"

    def go_to_thanks(self):
        self.root.current = "thanks"

    def go_to_subject(self, subject):
        self.current_subject = subject
        if subject == "varkt":
            self.current_section = ""
            self.refresh_lab_list()
            self.root.current = "lab_list"
        else:
            self.refresh_sections_list()
            self.root.current = "sections_list"

    def go_to_lab_list(self, section_name=None):
        if section_name:
            self.current_section = section_name
        self.refresh_lab_list()
        self.root.current = "lab_list"

    def go_to_add_lab(self):
        if self.admin_mode and self.current_subject != "varkt":
            self.root.current = "add_lab"
            Clock.schedule_once(lambda dt: self.update_section_menu_items(), 0.1)
        elif self.admin_mode and self.current_subject == "varkt":
            self.status_message = "Добавление лабораторных для ВАРКТ доступно только через редактирование JSON"

    def go_back_to_lab_list(self):
        self.refresh_lab_list()
        self.root.current = "lab_list"

    def go_back_to_subject_list(self):
        self.root.current = "menu"

    def toggle_theme(self, value):
        self.theme_cls.theme_style = "Dark" if value else "Light"

    def open_url(self, url):
        if url and url.strip():
            webbrowser.open(url)
        else:
            self.status_message = "Ссылка не указана"

    def get_subject_name(self, subject):
        names = {"physics": "Физика", "chemistry": "Химия", "varkt": "ВАРКТ"}
        return names.get(subject, subject)

    # ---------- Разделы (только физика/химия) ----------
    def refresh_sections_list(self):
        screen = self.root.get_screen("sections_list")
        screen.ids.sections_title.title = f"{self.get_subject_name(self.current_subject)} - Разделы"
        container = screen.ids.sections_container
        container.clear_widgets()
        sections = self.get_sections()
        for sec in sections:
            name = sec["name"]
            item = OneLineListItem(text=name)
            item.bind(on_release=lambda x, n=name: self.go_to_lab_list(n))
            container.add_widget(item)

    def get_sections(self):
        subject_data = self.data.get(self.current_subject, {})
        return subject_data.get("sections", [])

    def add_section(self, section_name):
        if not section_name or self.current_subject == "varkt":
            return
        subject_data = self.data.setdefault(self.current_subject, {})
        sections = subject_data.setdefault("sections", [])
        if any(s["name"] == section_name for s in sections):
            self.status_message = "Раздел уже существует"
            return
        sections.append({"name": section_name, "labs": {}})
        self.save_data_to_file()
        self.refresh_sections_list()

    def show_add_section_dialog(self):
        if not self.admin_mode or self.current_subject == "varkt":
            return
        text_field = MDTextField(hint_text="Название раздела")
        dialog = MDDialog(
            title="Новый раздел",
            type="custom",
            content_cls=text_field,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="Создать", on_release=lambda x: self._add_section_callback(dialog, text_field.text.strip())),
            ],
        )
        dialog.open()

    def _add_section_callback(self, dialog, name):
        dialog.dismiss()
        if name:
            self.add_section(name)

    # ---------- Лабораторные работы ----------
    def refresh_lab_list(self):
        screen = self.root.get_screen("lab_list")
        if self.current_subject == "varkt":
            screen.ids.lab_list_title.title = f"{self.get_subject_name('varkt')} - Лабораторные работы"
        else:
            screen.ids.lab_list_title.title = f"{self.get_subject_name(self.current_subject)} - {self.current_section}"
        container = screen.ids.container
        container.clear_widgets()
        labs_dict = self.get_labs_dict()
        if labs_dict:
            if self.current_subject == "varkt":
                for lab_id, lab_data in labs_dict.items():
                    title = lab_data.get("title", "")
                    item = OneLineListItem(text=title)
                    item.bind(on_release=lambda x, n=lab_id: self.open_varkt_lab(n))
                    container.add_widget(item)
            else:
                for name in sorted(labs_dict.keys(), key=str.lower):
                    item = OneLineListItem(text=name)
                    item.bind(on_release=lambda x, n=name: self.open_lab(n))
                    container.add_widget(item)

    def get_labs_dict(self):
        if self.current_subject == "varkt":
            subject_data = self.data.get("varkt", {})
            return subject_data.get("labs", {})
        else:
            sections = self.get_sections()
            for sec in sections:
                if sec["name"] == self.current_section:
                    return sec.get("labs", {})
            return {}

    def add_new_lab(self):
        if not self.admin_mode or self.current_subject == "varkt":
            if self.current_subject == "varkt":
                self.status_message = "Добавление лабораторных для ВАРКТ доступно только через редактирование JSON"
            return
        screen = self.root.get_screen("add_lab")
        name = screen.ids.new_name.text.strip()
        section = screen.ids.new_section.text.strip()
        goal = screen.ids.new_goal.text.strip()
        v1 = screen.ids.new_video1.text.strip()
        v2 = screen.ids.new_video2.text.strip()
        tools = screen.ids.new_tools.text.strip()
        qs = screen.ids.new_questions.text.strip()
        if not name or not v1 or not section:
            self.status_message = "Заполните название, раздел и ссылку видео 1"
            return

        sections = self.data.get(self.current_subject, {}).get("sections", [])
        found = False
        for sec in sections:
            if sec["name"] == section:
                sec["labs"][name] = {
                    "goal": goal,
                    "v1": v1,
                    "v2": v2,
                    "tools": tools,
                    "qs": qs
                }
                found = True
                break
        if not found:
            self.status_message = "Раздел не найден"
            return

        self.save_data_to_file()
        self.clear_add_lab_fields()
        self.refresh_lab_list()
        self.go_back_to_lab_list()

    def open_lab(self, name):
        labs = self.get_labs_dict()
        data = labs.get(name, {})
        self.current_lab_name = name
        self.current_lab_goal = data.get('goal', '')
        self.current_lab_tools = data.get('tools', '')
        self.current_lab_questions = data.get('qs', '')
        self.current_lab_v1 = data.get('v1', '')
        self.current_lab_v2 = data.get('v2', '')
        self.last_opened_lab = name
        self.last_opened_subject = self.current_subject
        self.last_opened_section = self.current_section
        self.root.current = "lab_details"

    def open_varkt_lab(self, lab_id):
        labs = self.get_labs_dict()
        data = labs.get(lab_id, {})
        self.current_varkt_title = data.get('title', '')
        self.current_varkt_prep = data.get('prep_materials', '')
        self.current_varkt_access = data.get('lab_access', '')
        self.last_opened_lab = lab_id
        self.last_opened_subject = self.current_subject
        self.last_opened_section = ""
        self.root.current = "varkt_lab_details"

    def clear_add_lab_fields(self):
        screen = self.root.get_screen("add_lab")
        for fid in ("new_name", "new_section", "new_goal", "new_video1", "new_video2", "new_tools", "new_questions"):
            try:
                screen.ids[fid].text = ""
            except:
                pass

    # ---------- Выпадающий список разделов (только физика/химия) ----------
    def update_section_menu_items(self):
        if self.current_subject == "varkt":
            return
        sections = self.get_sections()
        if not sections:
            return
        items = [{"text": sec["name"], "viewclass": "OneLineListItem",
                  "on_release": lambda x=sec["name"]: self.set_section_field(x)} for sec in sections]
        self.section_menu = MDDropdownMenu(
            caller=self.root.get_screen("add_lab").ids.new_section,
            items=items,
            max_height="200dp"
        )
        self.section_menu.open()

    def show_section_menu(self):
        if self.admin_mode and self.current_subject != "varkt":
            self.update_section_menu_items()

    def set_section_field(self, section_name):
        self.root.get_screen("add_lab").ids.new_section.text = section_name
        if self.section_menu:
            self.section_menu.dismiss()

    # ---------- Методички ----------
    def refresh_manuals_list(self):
        screen = self.root.get_screen("manuals")
        cont = screen.ids.manuals_container
        cont.clear_widgets()
        manuals = self.manuals_data.get(self.current_subject, [])
        for i, m in enumerate(manuals):
            box = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing="10dp", padding="5dp")
            btn = MDRaisedButton(
                text=m["title"], icon="book-open-page-variant", size_hint_x=0.7,
                on_release=lambda x, url=m["url"]: self.open_url(url)
            )
            box.add_widget(btn)
            if self.admin_mode:
                box.add_widget(MDIconButton(icon="pencil", on_release=lambda x, idx=i: self.edit_manual(idx)))
                box.add_widget(MDIconButton(icon="delete", on_release=lambda x, idx=i: self.delete_manual(idx)))
            cont.add_widget(box)

    def show_add_manual_dialog(self):
        if not self.admin_mode:
            return
        self.manual_title_field.text = ""
        self.manual_url_field.text = ""
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
        self.save_manuals_to_file()

    def delete_manual(self, idx):
        subj = self.current_subject
        if subj in self.manuals_data and 0 <= idx < len(self.manuals_data[subj]):
            del self.manuals_data[subj][idx]
            self.refresh_manuals_list()
            self.save_manuals_to_file()

    # ---------- Сохранение / загрузка методичек ----------
    def save_manuals_to_file(self):
        try:
            with open(self.manuals_data_path, "w", encoding="utf-8") as f:
                json.dump(self.manuals_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Ошибка сохранения методичек:", e)

    def load_manuals_from_file(self):
        if os.path.exists(self.manuals_data_path):
            try:
                with open(self.manuals_data_path, "r", encoding="utf-8") as f:
                    self.manuals_data = json.load(f)
            except Exception as e:
                print("Ошибка загрузки методичек:", e)

    # ---------- Импорт и сохранение основных данных ----------
    def save_data_to_file(self):
        try:
            with open(self.local_data_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"Данные сохранены в {self.local_data_path}")
        except Exception as e:
            print("Ошибка сохранения:", e)

    def _check_for_updates_background(self):
        """Фоновый поток: скачивает актуальный labs_data.json и обновляет приложение."""
        url = "https://raw.githubusercontent.com/vinpap2008S/FizoksProgect/master/labs_data.json"
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=15) as resp:
                raw = resp.read().decode('utf-8')
            new_data = json.loads(raw)
            if not isinstance(new_data, dict):
                return
            migrated = self.migrate_if_needed(new_data)
            self.data = migrated
            self.save_data_to_file()
            Clock.schedule_once(lambda dt: self.post_load())
            Clock.schedule_once(lambda dt: self._update_status("База данных обновлена из сети"))
        except Exception as e:
            print("Ошибка фонового обновления:", e)

    def try_import_with_retry(self, attempt=0):
        self.retry_attempt = attempt
        # 1. Всегда сначала загружаем локальный файл (мгновенный старт)
        if os.path.exists(self.local_data_path):
            try:
                with open(self.local_data_path, "r", encoding="utf-8") as f:
                    local_data = json.load(f)
                self.data = self.migrate_if_needed(local_data)
                self.load_manuals_from_file()
                Clock.schedule_once(lambda dt: self.post_load())
                Clock.schedule_once(lambda dt: self._update_status("Данные загружены из локального файла"))
            except Exception as e:
                print("Ошибка загрузки локального JSON:", e)

            # 2. В фоне пытаемся скачать свежую версию
            threading.Thread(target=self._check_for_updates_background, daemon=True).start()
            return

        # Если локального файла нет — пробуем скачать из сети (как раньше)
        url = "https://raw.githubusercontent.com/vinpap2008S/FizoksProgect/master/labs_data.json"
        def download_and_process():
            try:
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req, timeout=15) as resp:
                    raw = resp.read().decode('utf-8')
                data = json.loads(raw)
                if isinstance(data, dict):
                    migrated = self.migrate_if_needed(data)
                    self.data = migrated
                    self.save_data_to_file()
                    self.load_manuals_from_file()
                    Clock.schedule_once(lambda dt: self.post_load())
                    Clock.schedule_once(lambda dt: self._update_status("Данные успешно загружены из сети"))
                else:
                    raise ValueError("Некорректный формат данных")
            except Exception as e:
                Clock.schedule_once(lambda dt: self._update_status("Не удалось загрузить данные из сети, используем пустую базу"))
                self.data = self.migrate_if_needed({})
                Clock.schedule_once(lambda dt: self.post_load())

        threading.Thread(target=download_and_process, daemon=True).start()

    def migrate_if_needed(self, data):
        allowed_subjects = ("physics", "chemistry", "varkt")
        if isinstance(data, dict) and any(subj in data for subj in allowed_subjects):
            new_data = {}
            for subj in allowed_subjects:
                if subj in data and isinstance(data[subj], dict):
                    new_data[subj] = data[subj].copy()
                    if subj == "varkt":
                        if "sections" in new_data[subj]:
                            all_labs = {}
                            for sec in new_data[subj]["sections"]:
                                all_labs.update(sec.get("labs", {}))
                            new_data[subj] = {"labs": all_labs}
                        elif "labs" not in new_data[subj]:
                            new_data[subj] = {"labs": {}}
                    else:
                        if "sections" not in new_data[subj]:
                            if "labs" in new_data[subj]:
                                new_data[subj]["sections"] = [{"name": "Основные", "labs": new_data[subj]["labs"]}]
                                del new_data[subj]["labs"]
                            else:
                                new_data[subj]["sections"] = []
                else:
                    if subj == "varkt":
                        new_data[subj] = {"labs": {}}
                    else:
                        new_data[subj] = {"sections": []}
            return new_data

        if "labs" in data:
            old_labs = data["labs"]
            new_data = {"physics": {"sections": []}, "chemistry": {"sections": []}, "varkt": {"labs": {}}}
            labs_by_subject = {"physics": {}, "chemistry": {}, "varkt": {}}
            for lab_name, lab_info in old_labs.items():
                subj = lab_info.get("subject", "physics")
                if subj not in labs_by_subject:
                    subj = "physics"
                clean_info = {k: v for k, v in lab_info.items() if k in ("goal", "v1", "v2", "tools", "qs")}
                labs_by_subject[subj][lab_name] = clean_info
            for subj in ("physics", "chemistry"):
                if labs_by_subject[subj]:
                    new_data[subj]["sections"].append({"name": "Основные", "labs": labs_by_subject[subj]})
            if "manuals" in data:
                self.manuals_data = data["manuals"]
            return new_data

        return {"physics": {"sections": []}, "chemistry": {"sections": []}, "varkt": {"labs": {}}}

    def post_load(self):
        self.refresh_sections_list()
        self.refresh_lab_list()
        self.refresh_manuals_list()

    def _update_status(self, message):
        self.status_message = message
        Clock.schedule_once(lambda dt: self._hide_status(), 5)

    def _hide_status(self):
        self.status_message = ""

    # ---------- Управление данными (админ-режим) ----------
    def show_data_management_dialog(self):
        if not self.admin_mode:
            return

        # Вертикальный контейнер для всех элементов
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding="10dp",
            adaptive_height=True
        )

        # Три кнопки вертикально, растянутые по ширине
        btn_update = MDRaisedButton(
            text="Скачать обновлённую базу",
            size_hint_x=1,
            size_hint_y=None,
            height="56dp"
        )
        btn_export = MDRaisedButton(
            text="Экспорт базы данных",
            size_hint_x=1,
            size_hint_y=None,
            height="56dp"
        )
        btn_path = MDRaisedButton(
            text="Показать путь к файлу",
            size_hint_x=1,
            size_hint_y=None,
            height="56dp"
        )

        main_layout.add_widget(btn_update)
        main_layout.add_widget(btn_export)
        main_layout.add_widget(btn_path)

        # Нижний ряд: кнопка «Закрыть» справа
        bottom_row = MDBoxLayout(
            orientation="horizontal",
            spacing="12dp",
            adaptive_height=True,
            size_hint_y=None,
            height="56dp",
            padding=[0, "12dp", 0, 0]  # небольшой отступ сверху
        )
        # Растягивающаяся пустота слева
        bottom_row.add_widget(MDBoxLayout(size_hint_x=1))
        btn_close = MDRaisedButton(
            text="Закрыть",
            md_bg_color=(0.8, 0.4, 0.2, 1.0),  # цвет как у кнопки ВАРКТ
            text_color=(1, 1, 1, 1),
            size_hint_x=None,
            size_hint_y=1,
            width="120dp"
        )
        bottom_row.add_widget(btn_close)
        main_layout.add_widget(bottom_row)

        # Создаём диалог
        dialog = MDDialog(
            title="Управление базой данных",
            type="custom",
            content_cls=main_layout,
            buttons=[],  # стандартные кнопки не используем
        )

        # Привязываем действия
        btn_update.bind(on_release=lambda x: self._force_update_and_close(dialog))
        btn_export.bind(on_release=lambda x: self._start_export_and_close(dialog))
        btn_path.bind(on_release=lambda x: self._show_path_and_close(dialog))
        btn_close.bind(on_release=lambda x: dialog.dismiss())

        dialog.open()

    def _force_update_and_close(self, dialog):
        dialog.dismiss()
        if not self.admin_mode:
            return
        self.status_message = "Запущено обновление базы данных..."
        threading.Thread(target=self._check_for_updates_background, daemon=True).start()

    def _start_export_and_close(self, dialog):
        dialog.dismiss()
        if not self.admin_mode:
            return
        self.file_manager.select_path = self.export_data_callback
        self.file_manager.show(os.path.expanduser("~"))

    def export_data_callback(self, path):
        try:
            if os.path.exists(self.local_data_path):
                shutil.copy2(self.local_data_path, os.path.join(path, 'labs_data.json'))
            if os.path.exists(self.manuals_data_path):
                shutil.copy2(self.manuals_data_path, os.path.join(path, 'manuals_data.json'))
            self.status_message = f"База данных экспортирована в: {path}"
        except Exception as e:
            self.status_message = f"Ошибка экспорта: {e}"
        finally:
            self.file_manager.close()

    def _show_path_and_close(self, dialog):
        dialog.dismiss()
        path = self.local_data_path
        Clipboard.copy(path)  # Копируем путь в буфер обмена
        self.status_message = f"Файл базы данных: {path} (путь скопирован в буфер обмена)"

    def on_stop(self):
        if self.retry_timer:
            self.retry_timer.cancel()

    def exit_manager_callback(self, *args):
        self.file_manager.close()

    def select_path_callback(self, path):
        pass


if __name__ == "__main__":
    LabApp().run()
