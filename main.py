from website import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False)  # use_reloader=False to avoid re-running the app during debug mode
# 