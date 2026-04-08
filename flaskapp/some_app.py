from flask import Flask
import sys

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    # Для CI: запускаем и даем поработать 10 секунд, затем выходим
    import threading
    import time

    def shutdown():
        time.sleep(10)
        sys.exit(0)

    threding.Thread(target = shutdown, daemon = True).start()
    app.run(host='0.0.0.0', port=5000)
