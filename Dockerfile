# Use official Python image as base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run the application
CMD ["gunicorn", "stock_analysis_project.wsgi:application", "--bind", "0.0.0.0:8000"]
