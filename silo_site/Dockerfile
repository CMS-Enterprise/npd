FROM python:3.14.4-slim-trixie

WORKDIR /app
# Copy and install app dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the flask app
COPY app.py .
# Copy the frontend
ADD static ./static
# Run the app on 8080
EXPOSE 8080/tcp
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]