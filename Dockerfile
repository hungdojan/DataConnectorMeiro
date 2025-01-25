FROM docker.io/library/python:3.9

RUN mkdir /recover_dir
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENV MIN_AGE=18 \
    FAILED_RECORDS_DIRPATH=/recover_dir \
    PYTHONPATH=/app/src

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--chdir", "src", "wsgi:app"]
