FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY setting.toml config.json accounts.json tool.py /app/
RUN pip install --no-cache-dir streamlit pandas openpyxl

CMD ["streamlit", "run", "/app/tool.py"]