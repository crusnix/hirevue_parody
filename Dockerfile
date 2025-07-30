# 1. Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Install system dependencies if any
# RUN apt-get update && apt-get install -y ...

# 5. Install Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the application code into the container
COPY . /app

# 7. Expose the port the app runs on
EXPOSE 8000

# 8. Run the uvicorn server
# The --host 0.0.0.0 is crucial for it to be accessible from outside the container.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]