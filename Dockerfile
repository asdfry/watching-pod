FROM python:3.7-slim

WORKDIR /workspace

COPY ./app /workspace/app

RUN pip install --no-cache-dir --upgrade -r /workspace/app/requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
