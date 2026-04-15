FROM python:3.14.4-slim-trixie

WORKDIR app
# Copy the flask app
COPY requirements.txt .
COPY app.py .

# Copy the frontend
ADD static static

# Install dependencies
RUN pip install -r requirements.txt

# Run the app
CMD ["./app.py"]