# Use the official Python runtime image
FROM python:3.13-slim AS builder
 
# Create the app directory
RUN mkdir /app

# Set the working directory inside the container
WORKDIR /app
 
# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 


RUN apt-get update \
    && apt-get -y install binutils libproj-dev gdal-bin


# Upgrade pip
RUN pip install --upgrade pip
 
# Copy the Django project  and install dependencies
COPY requirements.txt  /app/
    
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin

# Set up a virtual environment in the builder stage
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python requirements into the virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

 
# Stage 2: Production stage
FROM python:3.13-slim
 
RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app

# Install only the *runtime* system dependencies for GDAL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the PATH to include the virtual environment's bin directory
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory
WORKDIR /app
 
# Copy application code
COPY --chown=appuser:appuser . .
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Switch to non-root user
USER appuser
 
# Expose the application port
EXPOSE 8000 

# In production, collect static assets then start gunicorn in entrypoint.sh
# Note that this behavior is disabled for local dev by updating entrypoint in compose.yml
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "app.wsgi:application"]