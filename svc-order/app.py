# app.py

from flask import Flask
from infrastructure.api.routes import bp
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

metrics = PrometheusMetrics(app)

metrics.info("svc_order_info", "Service order info", version="1.0.0")

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
