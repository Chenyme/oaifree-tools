FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY setting.toml config.json accounts.json invite.json login.py style.css /app/
RUN pip install --no-cache-dir streamlit pandas openpyxl streamlit-on-Hover-tabs

CMD ["streamlit", "run", "/app/login.py"]