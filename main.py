from __future__ import annotations

import json
import os
import threading
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

KV = r'''
#:import dp kivy.metrics.dp

<RootView>:
    orientation: 'vertical'
    padding: dp(16), dp(12)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: (0.015, 0.015, 0.02, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(8)
        Label:
            text: 'VIVA AI'
            color: (1, 0.08, 0.08, 1)
            font_size: '22sp'
            bold: True
            halign: 'left'
            text_size: self.size
        Label:
            text: 'CRIMSON CORE'
            color: (0.45, 0.45, 0.5, 1)
            font_size: '10sp'
            bold: True
            halign: 'right'
            valign: 'middle'
            text_size: self.size
        Button:
            text: '•••'
            size_hint_x: None
            width: dp(42)
            background_normal: ''
            background_color: (0.10, 0.10, 0.13, 1)
            color: (1, 0.2, 0.2, 1)
            on_release: app.open_key_dialog()
    Label:
        text: 'Hello, জান'
        size_hint_y: None
        height: dp(28)
        color: (0.95, 0.95, 0.98, 1)
        font_size: '22sp'
        bold: True
        halign: 'left'
        text_size: self.size
    Label:
        text: 'How can I assist you today?'
        size_hint_y: None
        height: dp(22)
        color: (0.5, 0.5, 0.55, 1)
        font_size: '13sp'
        halign: 'left'
        text_size: self.size
    Label:
        id: orb
        text: '◉'
        size_hint_y: None
        height: dp(112)
        color: (1, 0.04, 0.04, 1)
        font_size: '92sp'
        bold: True
        halign: 'center'
        valign: 'middle'
        text_size: self.size
    Label:
        text: root.status
        size_hint_y: None
        height: dp(24)
        color: (1, 0.22, 0.22, 1)
        font_size: '12sp'
        halign: 'center'
        text_size: self.size
    GridLayout:
        cols: 2
        size_hint_y: None
        height: dp(88)
        spacing: dp(7)
        Button:
            text: 'VOICE MODE\nTap to speak'
            background_normal: ''
            background_color: (0.09, 0.07, 0.08, 1)
            color: (1, 0.35, 0.35, 1)
            on_release: app.start_speech()
        Button:
            text: 'NEURAL LENS\nLive camera vision'
            background_normal: ''
            background_color: (0.09, 0.07, 0.08, 1)
            color: (1, 0.35, 0.35, 1)
            on_release: app.toggle_live_vision()
    Camera:
        id: camera
        resolution: (640, 480)
        play: False
        size_hint_y: None
        height: dp(175) if root.live_vision else 0
        opacity: 1 if root.live_vision else 0
    ScrollView:
        id: scroll
        do_scroll_x: False
        BoxLayout:
            id: messages
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(7)
            padding: dp(2)
    Label:
        text: root.status
        size_hint_y: None
        height: dp(20)
        color: (0.45, 0.45, 0.5, 1)
        font_size: '10sp'
        halign: 'left'
        text_size: self.size
    BoxLayout:
        size_hint_y: None
        height: dp(54)
        spacing: dp(6)
        TextInput:
            id: question
            hint_text: 'Ask Viva anything...'
            multiline: False
            background_normal: ''
            background_color: (0.08, 0.08, 0.11, 1)
            foreground_color: (0.95, 0.95, 0.98, 1)
            cursor_color: (1, 0.1, 0.1, 1)
            padding: dp(12), dp(15)
            on_text_validate: app.ask_text(self.text)
        Button:
            text: '➤'
            size_hint_x: None
            width: dp(54)
            background_normal: ''
            background_color: (0.85, 0.03, 0.03, 1)
            color: (1, 1, 1, 1)
            font_size: '24sp'
            on_release: app.ask_text(question.text)
    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(8)
        Button:
            text: 'CAMERA'
            background_normal: ''
            background_color: (0.1, 0.08, 0.09, 1)
            color: (1, 0.35, 0.35, 1)
            on_release: app.toggle_live_vision()
        Button:
            text: 'MICROPHONE'
            background_normal: ''
            background_color: (0.85, 0.03, 0.03, 1)
            color: (1, 1, 1, 1)
            on_release: app.start_speech()
'''
Builder.load_string(KV)


class RootView(BoxLayout):
    status = StringProperty('Viva প্রস্তুত')
    live_vision = BooleanProperty(False)


class VivaGeminiApp(App):
    title = 'Viva AI Gemini'

    def build(self):
        self.root_view = RootView()
        self.history = []
        self.vision_event = None
        self.last_vision_answer = ''
        self.orb_animation = None
        Clock.schedule_once(self.start_orb_animation, 0.4)
        self.app_dir = Path(self.user_data_dir)
        self.key_file = self.app_dir / 'gemini_api_key.txt'
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.commands = self.load_commands()
        return self.root_view

    def load_commands(self):
        """Load editable commands from app-private storage, then project assets."""
        user_file = self.app_dir / 'commands.json'
        asset_file = Path(__file__).with_name('commands.json')
        if not user_file.exists() and asset_file.exists():
            try:
                user_file.write_text(asset_file.read_text(encoding='utf-8'), encoding='utf-8')
            except OSError:
                pass
        try:
            source = user_file if user_file.exists() else asset_file
            data = json.loads(source.read_text(encoding='utf-8'))
            commands = data.get('commands', [])
            return commands if isinstance(commands, list) else []
        except (OSError, ValueError, TypeError):
            self.set_status('commands.json পড়া যায়নি')
            return []

    def find_custom_command(self, text):
        query = text.strip().casefold()
        for command in self.commands:
            if not isinstance(command, dict):
                continue
            phrases = command.get('phrases', [])
            mode = command.get('match', 'exact')
            for phrase in phrases if isinstance(phrases, list) else []:
                phrase = str(phrase).strip().casefold()
                matched = query == phrase if mode == 'exact' else phrase in query
                if matched:
                    return command
        return None

    def start_orb_animation(self, _dt=0):
        if not self.root_view.ids.get('orb'):
            return
        self.orb_animation = Animation(font_size=104, opacity=0.72, duration=0.9) + Animation(font_size=92, opacity=1, duration=0.9)
        self.orb_animation.repeat = True
        self.orb_animation.start(self.root_view.ids.orb)

    def api_key(self):
        try:
            return self.key_file.read_text(encoding='utf-8').strip()
        except FileNotFoundError:
            return ''

    def open_key_dialog(self):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput

        box = BoxLayout(orientation='vertical', padding=12, spacing=8)
        field = TextInput(text=self.api_key(), hint_text='Gemini API key', password=True, multiline=False)
        save = Button(text='SAVE', size_hint_y=None, height=48)
        box.add_widget(field)
        box.add_widget(save)
        popup = Popup(title='Gemini API Key', content=box, size_hint=(.92, .35), auto_dismiss=True)

        def save_key(_):
            key = field.text.strip()
            if key:
                self.app_dir.mkdir(parents=True, exist_ok=True)
                self.key_file.write_text(key, encoding='utf-8')
                try:
                    self.key_file.chmod(0o600)
                except OSError:
                    pass
                self.set_status('Gemini API key সংরক্ষিত')
            popup.dismiss()

        save.bind(on_release=save_key)
        popup.open()

    def set_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.root_view, 'status', text), 0)

    def toggle_live_vision(self):
        if self.root_view.live_vision:
            self.stop_live_vision()
        else:
            self.start_live_vision()

    def start_live_vision(self):
        if platform != 'android':
            self.set_status('Live camera শুধু Android APK-তে কাজ করবে')
            return
        self.root_view.live_vision = True
        self.root_view.ids.camera.play = True
        self.set_status('Live Vision চালু — frame বিশ্লেষণ হচ্ছে')
        self.vision_event = Clock.schedule_interval(self.capture_vision_frame, 4.0)

    def stop_live_vision(self):
        if self.vision_event:
            self.vision_event.cancel()
            self.vision_event = None
        self.root_view.ids.camera.play = False
        self.root_view.live_vision = False
        self.set_status('Live Vision বন্ধ')

    def capture_vision_frame(self, _dt):
        camera = self.root_view.ids.camera
        if not camera.texture or not self.api_key():
            return
        frame = self.app_dir / 'live_frame.png'
        try:
            camera.texture.save(str(frame), flipped=False)
            threading.Thread(target=self._vision_worker, args=(frame,), daemon=True).start()
        except Exception as exc:
            self.set_status(f'Camera frame নেওয়া যায়নি: {exc}')

    def _vision_worker(self, frame):
        try:
            answer = analyze_image(self.api_key(), frame)
            if answer and answer != self.last_vision_answer:
                self.last_vision_answer = answer
                Clock.schedule_once(lambda dt: self.finish_vision(answer), 0)
        except Exception as exc:
            Clock.schedule_once(lambda dt: self.set_status(f'Vision error: {exc}'), 0)

    def finish_vision(self, answer):
        self.add_message('Viva Vision', answer)
        self.set_status('Live Vision চালু — পরের frame-এর অপেক্ষায়')
        speak_android(answer)

    def add_message(self, who, text):
        from kivy.uix.label import Label
        color = (0.95, 0.2, 0.7, 1) if who == 'আপনি' else (0.75, 0.95, 1, 1)
        label = Label(
            text=f'{who}: {text}',
            color=color,
            font_size='16sp',
            halign='left',
            valign='top',
            size_hint_y=None,
            text_size=(self.root_view.width - 28, None),
        )
        label.bind(texture_size=lambda widget, size: setattr(widget, 'height', size[1] + 14))
        self.root_view.ids.messages.add_widget(label)
        Clock.schedule_once(lambda dt: setattr(self.root_view.ids.scroll, 'scroll_y', 0), 0.05)

    def ask_text(self, text):
        text = (text or '').strip()
        self.root_view.ids.question.text = ''
        if not text:
            return
        self.add_message('আপনি', text)
        custom = self.find_custom_command(text)
        if custom:
            answer = str(custom.get('reply', 'জান, আপনার custom command চালাচ্ছি।'))
            action = dict(custom.get('action') or {})
            action['_query'] = text
            self.finish_answer(answer, action)
            return
        self.set_status('Gemini ভাবছে...')
        threading.Thread(target=self._ask_worker, args=(text,), daemon=True).start()

    def _ask_worker(self, text):
        try:
            answer, action = ask_gemini(self.api_key(), self.history, text)
            self.history.extend([
                {'role': 'user', 'parts': [{'text': text}]},
                {'role': 'model', 'parts': [{'text': answer}]},
            ])
            Clock.schedule_once(lambda dt: self.finish_answer(answer, action), 0)
        except Exception as exc:
            Clock.schedule_once(lambda dt: self.finish_answer(f'জান, Gemini API সমস্যা: {exc}', None), 0)

    def finish_answer(self, answer, action):
        self.add_message('Viva', answer)
        self.set_status('Viva প্রস্তুত')
        run_action(action)
        speak_android(answer)

    def start_speech(self):
        if platform != 'android':
            self.set_status('Speech input শুধু Android APK-তে কাজ করবে')
            return
        try:
            from android import activity
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            RecognizerIntent = autoclass('android.speech.RecognizerIntent')
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, 'bn-BD')
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            activity.bind(on_activity_result=self.on_speech_result)
            PythonActivity.mActivity.startActivityForResult(intent, 9173)
            self.set_status('বাংলায় কথা বলুন...')
        except Exception as exc:
            self.set_status(f'Microphone শুরু হয়নি: {exc}')

    def on_speech_result(self, request_code, result_code, intent):
        if request_code != 9173:
            return
        try:
            results = intent.getStringArrayListExtra('android.speech.extra.RESULTS')
            if results and results.size() > 0:
                self.ask_text(results.get(0))
        finally:
            try:
                from android import activity
                activity.unbind(on_activity_result=self.on_speech_result)
            except Exception:
                pass


def ask_gemini(key, history, question):
    if not key:
        raise RuntimeError('Settings থেকে Gemini API key দিন')
    system = (
        'তুমি Viva, একজন বন্ধুসুলভ বাংলা voice assistant। ব্যবহারকারীকে জান বলে '
        'সম্বোধন করো এবং স্বাভাবিক সংক্ষিপ্ত বাংলায় উত্তর দাও। নিরাপদ phone action চাইলে '
        'শুরুতে একটি token দাও: [ACTION:OPEN_YOUTUBE], [ACTION:OPEN_CHROME], '
        '[ACTION:OPEN_SETTINGS], [ACTION:YOUTUBE_SEARCH:<query>], [ACTION:VOLUME_UP], '
        '[ACTION:VOLUME_DOWN]. Payment, delete, send, permission বা account action কোরো না।'
    )
    contents = [{'role': 'user', 'parts': [{'text': system}]}]
    contents.extend(history[-16:])
    contents.append({'role': 'user', 'parts': [{'text': question}]})
    model = os.getenv('VIVA_CHAT_MODEL', 'gemini-3.8-flash')
    response = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        params={'key': key},
        json={'contents': contents},
        timeout=60,
    )
    if not response.ok:
        raise RuntimeError(f'Gemini HTTP {response.status_code}: {response.text[:240]}')
    data = response.json()
    answer = data['candidates'][0]['content']['parts'][0]['text'].strip()
    match = __import__('re').search(r'\[ACTION:(.*?)\]', answer, flags=__import__('re').DOTALL)
    action = match.group(1).strip() if match else None
    answer = __import__('re').sub(r'\[ACTION:.*?\]', '', answer, flags=__import__('re').DOTALL).strip()
    if answer and 'জান' not in answer:
        answer = 'জান, ' + answer
    return answer or 'জান, আমি শুনছি।', action


def analyze_image(key, image_path):
    """Send one sampled camera frame to Gemini for scene/object understanding."""
    if not key:
        return ''
    model = os.getenv('VIVA_VISION_MODEL', os.getenv('VIVA_CHAT_MODEL', 'gemini-3.8-flash'))
    image_bytes = Path(image_path).read_bytes()
    import base64
    prompt = (
        'এই live camera frame বাংলায় বিশ্লেষণ করো। প্রথমে ১ লাইনে দৃশ্যের সারাংশ দাও। '
        'তারপর দৃশ্যমান গুরুত্বপূর্ণ object, লেখা, মানুষ বা সম্ভাব্য বাধা সংক্ষেপে বলো। '
        'নিশ্চিত না হলে অনুমান না করে বলবে যে নিশ্চিত নও। সর্বোচ্চ ৩টি ছোট বাক্য।'
    )
    payload = {
        'contents': [{
            'role': 'user',
            'parts': [
                {'text': prompt},
                {'inline_data': {'mime_type': 'image/png', 'data': base64.b64encode(image_bytes).decode('ascii')}},
            ],
        }],
    }
    response = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        params={'key': key},
        json=payload,
        timeout=60,
    )
    if not response.ok:
        raise RuntimeError(f'Gemini Vision HTTP {response.status_code}: {response.text[:220]}')
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text'].strip()


def speak_android(text):
    if platform != 'android':
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        tts = PythonActivity.mActivity.getSystemService(Context.TEXT_TO_SPEECH_SERVICE)
        tts.setLanguage(__import__('java.util', fromlist=['Locale']).Locale('bn', 'BD'))
        tts.speak(text, 0, None, 'viva-reply')
    except Exception:
        pass


def run_action(action):
    if not action:
        return
    if isinstance(action, dict):
        action_type = action.get('type')
        if action_type == 'reply':
            return
        if action_type == 'open_url':
            url = str(action.get('url', '')).strip()
            if url.startswith(('https://', 'http://')):
                webbrowser.open(url)
            return
        if action_type == 'youtube_search':
            source = action.get('_query', '').strip()
            prefix = str(action.get('prefix', '')).strip()
            query = source.replace(prefix, '', 1).strip() if prefix and prefix in source else source
            if query:
                webbrowser.open(f'https://youtube.com/results?search_query={quote_plus(query)}')
            return
        if platform == 'android' and action_type in {'open_settings', 'volume_up', 'volume_down', 'open_app'}:
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Context = autoclass('android.content.Context')
                activity = PythonActivity.mActivity
                if action_type == 'open_settings':
                    activity.startActivity(Intent('android.settings.SETTINGS'))
                elif action_type == 'open_app':
                    package_name = str(action.get('package', '')).strip()
                    launch = activity.getPackageManager().getLaunchIntentForPackage(package_name)
                    if launch:
                        activity.startActivity(launch)
                else:
                    audio = activity.getSystemService(Context.AUDIO_SERVICE)
                    AudioManager = autoclass('android.media.AudioManager')
                    direction = AudioManager.ADJUST_RAISE if action_type == 'volume_up' else AudioManager.ADJUST_LOWER
                    audio.adjustStreamVolume(AudioManager.STREAM_MUSIC, direction, AudioManager.FLAG_SHOW_UI)
            except Exception:
                pass
            return
    if action == 'OPEN_YOUTUBE':
        webbrowser.open('https://youtube.com')
    elif action == 'OPEN_CHROME':
        webbrowser.open('https://google.com')
    elif action.startswith('YOUTUBE_SEARCH:'):
        query = quote_plus(action.split(':', 1)[1].strip())
        webbrowser.open(f'https://youtube.com/results?search_query={query}')
    elif action in {'VOLUME_UP', 'VOLUME_DOWN', 'OPEN_SETTINGS'}:
        # These require a small Android JNI action bridge in the next iteration.
        pass


if __name__ == '__main__':
    VivaGeminiApp().run()
