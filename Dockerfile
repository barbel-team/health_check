FROM python:3.8-slim-buster
COPY . /app
ADD ./process.sh /tmp/process.sh
WORKDIR /app
RUN pip install Flask
RUN pip install requests
RUN apt-get update && apt-get install curl -y

# RUN chmod +x /tmp/process.sh
# ENTRYPOINT ["sh", "/tmp/process.sh" ]
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
