FROM python:3.9-slim-buster

WORKDIR \flaskapiproject

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENV FLASK_APP=main.py
CMD ["flask", "run", "--host=0.0.0.0"]