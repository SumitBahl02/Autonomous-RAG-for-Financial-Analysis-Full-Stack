# Use an official Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose any necessary ports (if applicable, e.g., if there’s a web interface or API)
EXPOSE 8080

# Define environment variables (if needed)
ENV PYTHONUNBUFFERED=1

# Run the main script to start the application
CMD ["python", "main.py"]
