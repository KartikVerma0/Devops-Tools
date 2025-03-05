FROM python:3.11.9-slim-bullseye
COPY update_swagger.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt update
RUN apt install curl -y
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash