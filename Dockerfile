# 1. basic python image
FROM python:3.11-slim

# 2. working directory
WORKDIR /app

# 3. installing requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. copy project
COPY . .

# 5. ipenin port
EXPOSE 8080

# 6. run django with gunicorn
CMD exec gunicorn weather_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2
