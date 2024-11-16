import os
from website import create_app, socketio

app = create_app()

if __name__ == "__main__":
    import eventlet
    eventlet.monkey_patch()  # Ensure compatibility with Eventlet
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))