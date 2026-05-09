import sys
import os
import json
import mss
import mss.tools
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QUrl, pyqtSlot, pyqtSignal, QObject
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
import keyboard

from llm import GroqClient

class HotkeySignaler(QObject):
    trigger = pyqtSignal()

class ApiBridge(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.client = None
        self.pending_image_paths = []
        self.snip_counter = 0
        self.load_config()

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                data = json.load(f)
                if 'groq_api_key' in data:
                    self.client = GroqClient(data['groq_api_key'])
                self.config_data = data
        except FileNotFoundError:
            self.config_data = {}

    @pyqtSlot()
    def request_config(self):
        name = self.config_data.get('name', '')
        theme = self.config_data.get('theme', 'light')
        has_keys = 'groq_api_key' in self.config_data
        has_keys_str = 'true' if has_keys else 'false'
        self.main_window.webview.page().runJavaScript(f"window.applyConfig('{name}', '{theme}', '{has_keys_str}');")

    @pyqtSlot(str, str, str)
    def save_config_data(self, name, theme, groq_key):
        self.config_data = {'name': name, 'theme': theme, 'groq_api_key': groq_key}
        with open('config.json', 'w') as f:
            json.dump(self.config_data, f)
        self.client = GroqClient(groq_key)
        print("Config Saved.")

    @pyqtSlot()
    def ready(self):
        print("UI Ready. Registering hotkey Alt+S")
        keyboard.add_hotkey('alt+s', self.main_window.signaler.trigger.emit, suppress=True)

    @pyqtSlot(int, int, int, int)
    def capture_region(self, x, y, w, h):
        print(f"Capturing region: {x}, {y}, {w}x{h}")
        try:
            with mss.mss() as sct:
                monitor = {"top": y, "left": x, "width": w, "height": h}
                self.snip_counter += 1
                output = f"current_snip_{self.snip_counter}.png"
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
                self.pending_image_paths.append(os.path.abspath(output))
            
            self.main_window.webview.page().runJavaScript(f"window.onCaptureComplete({x}, {y}, {w}, {h});")
        except Exception as e:
            print(f"Capture error: {e}")

    @pyqtSlot(str, result=str)
    def ask(self, question):
        if not self.client:
            return "Error: Groq API Key not set."
        print(f"Asking Groq: {question} with {len(self.pending_image_paths)} images")
        ans = self.client.ask(question, self.pending_image_paths)
        self.pending_image_paths.clear()
        return ans

    @pyqtSlot()
    def hide_all(self):
        print("Hiding window & resetting session")
        self.pending_image_paths.clear()
        if self.client:
            self.client.reset_chat()
        self.main_window.hide()

    @pyqtSlot(str)
    def set_clickable_rects(self, rects_json):
        from PyQt6.QtGui import QRegion
        from PyQt6.QtCore import QRect
        
        if rects_json == 'full':
            self.main_window.clearMask()
            return
        
        region = QRegion()
        try:
            rects = json.loads(rects_json)
            for r in rects:
                if r['w'] > 0 and r['h'] > 0:
                    region = region.united(QRegion(QRect(r['x'], r['y'], r['w'], r['h'])))
            
            if region.isEmpty():
                self.main_window.setMask(QRegion(0, 0, 1, 1))
            else:
                self.main_window.setMask(region)
        except Exception as e:
            print(f"Error parsing rects: {e}")

class SnipyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.webview = QWebEngineView(self)
        self.webview.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.webview.page().setBackgroundColor(Qt.GlobalColor.transparent)
        
        self.channel = QWebChannel()
        self.api = ApiBridge(self)
        self.channel.registerObject('api', self.api)
        self.webview.page().setWebChannel(self.channel)

        self.signaler = HotkeySignaler()
        self.signaler.trigger.connect(self.trigger_snip)

        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "ui.html"))
        self.webview.setUrl(QUrl.fromLocalFile(html_path))
        self.webview.loadFinished.connect(self.inject_bridge)
        self.setCentralWidget(self.webview)

    def inject_bridge(self):
        script = """
        if (typeof QWebChannel !== 'undefined') {
            new QWebChannel(qt.webChannelTransport, function (channel) {
                window.pywebview = { api: channel.objects.api };
                if (window.onBridgeReady) window.onBridgeReady();
            });
        }
        """
        self.webview.page().runJavaScript(script)

    def trigger_snip(self):
        print("Hotkey triggered")
        self.show()
        self.raise_()
        self.activateWindow()
        self.webview.page().runJavaScript("window.startSnipMode();")

    def changeEvent(self, event):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.ActivationChange:
            if self.isActiveWindow():
                self.webview.page().runJavaScript("if(window.onFocusGained) window.onFocusGained();")
            else:
                self.webview.page().runJavaScript("if(window.onFocusLoss) window.onFocusLoss();")
        super().changeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = SnipyWindow()
    
    config_path = 'config.json'
    show_onboarding = True
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                if data.get('groq_api_key'):
                    show_onboarding = False
        except:
            pass
    
    if show_onboarding:
        window.show()
    
    sys.exit(app.exec())
