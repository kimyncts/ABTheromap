# Utiliser une image légère de Python
FROM python:3.11-slim

# Installer les dépendances système nécessaires
# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*


# Télécharger et installer BLAST+
RUN wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.16.0+-x64-linux.tar.gz \
    && tar -xvzf ncbi-blast-2.16.0+-x64-linux.tar.gz \
    && mv ncbi-blast-2.16.0+/bin/* /usr/local/bin/ \
    && rm -rf ncbi-blast-2.16.0+-x64-linux.tar.gz ncbi-blast-2.16.0+

# Définir le répertoire de travail
WORKDIR /app

# Copier requirements.txt depuis la racine du projet vers le conteneur
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet dans le conteneur
COPY ./src .

# Ouvrir le port 8000 (celui de Django)
EXPOSE 8000

# Commande de démarrage par défaut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
