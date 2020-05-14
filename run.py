from werkzeug.serving import run_simple
from project import app_dash


if __name__ == '__main__':
    # app.run(debug=True)
    run_simple('localhost', 5000, app_dash, use_reloader=True, use_debugger=True)