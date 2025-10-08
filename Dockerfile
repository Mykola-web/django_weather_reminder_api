# 1. basic python image
FROM python:3.11-slim

# 2. working directory
WORKDIR /app

# 3. installing requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. copy project
COPY . .

# 5. collect static files (WhiteNoise)
RUN python manage.py collectstatic --noinput

# 6. make entrypoint.sh executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 7. expose port (Cloud Run uses $PORT)
EXPOSE 8080

# 8. run entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# 9. default CMD for Gunicorn
CMD ["gunicorn", "weather_project.wsgi:application", "--bind", "0.0.0.0:${PORT:-8080}", "--workers", "2"]

