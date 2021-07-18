from dotenv import load_dotenv
from flask.cli import FlaskGroup
from project import main

app = main.app

cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()