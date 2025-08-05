FROM python:3.8

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY data/ /app/data/
COPY models/ /app/models/
COPY scripts/ /app/scripts/
COPY config/ /app/config/
COPY src/main.py /app/src/main.py

RUN mkdir -p ~/.streamlit/; echo "[general]"  > ~/.streamlit/credentials.toml; echo "email = \"\""  >> ~/.streamlit/credentials.toml

CMD ["python", "/app/src/API.py --mode server"]