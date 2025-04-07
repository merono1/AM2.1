# Usa una imagen oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que usará Flask
EXPOSE 8080

# Comando para arrancar tu app con gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app_web:app"]
