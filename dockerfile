FROM python:3.12-alpine

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . .

# RUN python -m pip install -r requirements.txt

EXPOSE 3000

# ENTRYPOINT ["python", "main_server_multy_thread.py"]

CMD ["python", "main_server_multy_thread.py"]

# /Users/oleksandrkharchenko/Downloads/my_storage  /app/storage - аргументі для внешней папки