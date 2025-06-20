FROM python:3.13.1

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y postgresql-client


# Installer les dépendances Python
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]