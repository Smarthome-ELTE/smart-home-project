# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories if they don't exist
RUN mkdir -p /app/db /app/Heating

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose ports (for future web interface)
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]