
from waitress import serve
from src import create_app


application = create_app()

if __name__ == '__main__':
    print("starting server")

    serve(application, listen='*:8000')
