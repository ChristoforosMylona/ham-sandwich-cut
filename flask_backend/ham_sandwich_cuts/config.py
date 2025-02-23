import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mydefaultsecretkey')  # Use environment variable or default
    SAMPLE_FILE_DIR = os.path.join(os.getcwd(), 'sample_files')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'  # Load DEBUG from environment variable
