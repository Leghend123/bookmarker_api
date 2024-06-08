from waitress import serve
from src import create_app


application = create_app()

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000
    url = f"http://{host}:{port}"

    debug_mode = application.debug
    debug_status = "ON" if debug_mode else "OFF"
    application.logger.info(f"DEBUG Mode:  {debug_status}")
    application.logger.info(f"Starting server at {url}")
    serve(application, listen=f'{host}:{port}')
