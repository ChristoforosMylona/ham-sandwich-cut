# Use the official Python image as the base
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file from the 'ham_sandwich_cuts' directory and install dependencies
COPY ham_sandwich_cuts/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from the 'ham_sandwich_cuts' directory
COPY ham_sandwich_cuts /app/

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
