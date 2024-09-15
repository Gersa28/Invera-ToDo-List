# Use the official Python image as the base image
FROM python:3.11.2

# Disables output buffering so that Python logs are displayed in real-time
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Copy only the requirements file first, for caching purposes
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the project files into the container
COPY ./ ./ 

# Expose port 8000 (default for Django development server)
EXPOSE 8000

# Run database migrations and then start the Django development server
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
