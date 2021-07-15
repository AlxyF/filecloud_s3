from dotenv import load_dotenv
from flask.cli import FlaskGroup
from project import main
import os

load_dotenv()
VOLUME_FILES = os.getenv('VOLUME_FILES')
print(VOLUME_FILES) #, flush=True)

main.volume_path = VOLUME_FILES

app = main.app

cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()