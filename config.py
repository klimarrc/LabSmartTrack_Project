import os

# use os.environ mapping for environment variables
env = os.environ

SECRET_KEY = env.get("SECRET_KEY")
DATABASE_URL = env.get("DATABASE_URL")
SMTP_HOST = env.get("SMTP_HOST")
SMTP_PORT = env.get("SMTP_PORT")
SUPERVISOR_EMAIL = env.get("SUPERVISOR_EMAIL")
