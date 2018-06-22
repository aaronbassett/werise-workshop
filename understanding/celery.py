import os
from celery import Celery

app = Celery(
    "understanding", broker=os.environ["BROKER_URL"], include=["understanding.tasks"]
)

if __name__ == "__main__":
    app.start()
