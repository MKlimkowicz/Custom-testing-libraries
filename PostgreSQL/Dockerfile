FROM python:3.9

WORKDIR /app

# Install necessary utilities and PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY ./app /app
COPY requirements.txt .
COPY wait-for.sh /wait-for.sh
RUN chmod +x /wait-for.sh

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
