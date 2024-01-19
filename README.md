docker build -t website:v1 .
docker run --env-file env website:v1 sh -c "python manage.py collectstatic --noinput"
docker run --env-file env -p 80:8000 website:v1
