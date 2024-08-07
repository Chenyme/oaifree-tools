FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .

ENV TZ=Asia/Shanghai

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "/app/home.py"]