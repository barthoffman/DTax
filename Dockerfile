# Belastingen-dashboard — dependency-vrij (Python-stdlib). Moderne Python i.p.v. de
# oude systeem-Python op de host. .env en authdata/ worden bij het draaien gemount
# (secrets/data komen NIET in de image — zie .dockerignore).
FROM python:3.12-slim

WORKDIR /app/rekenkern
COPY rekenkern/ /app/rekenkern/

ENV HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["python3", "api.py"]
