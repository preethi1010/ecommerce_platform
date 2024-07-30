# Base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 5000 for the Flask application
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run the Flask application
CMD ["flask", "run"]