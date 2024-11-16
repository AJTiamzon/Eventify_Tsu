from gevent import monkey
monkey.patch_all()  # Required for gevent compatibility
from website import create_app, socketio
import os

app = create_app()

if __name__ == "__main__":
    # Enable logging to debug WebSocket issues
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, logger=True, engineio_logger=True)
