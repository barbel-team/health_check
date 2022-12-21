FROM python:3.8-slim-buster
COPY . /app
WORKDIR /app
RUN pip install Flask
RUN pip install requests
RUN apt-get update && apt-get install curl -y
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
