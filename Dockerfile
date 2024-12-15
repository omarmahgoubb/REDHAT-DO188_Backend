# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Expose port 5000 to the host (default Flask port)
EXPOSE 5000

# Set environment variables to handle MongoDB connection and Flask's debug mode
ENV MONGO_URI=mongodb://mymongo:27017/package_tracking_system
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask application using the flask CLI (for development)
CMD ["flask", "run"]
