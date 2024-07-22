FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add Flask and SQLAlchemy to the requirements
RUN pip install --no-cache-dir Flask Flask-SQLAlchemy Werkzeug psycopg2-binary Flask-Migrate

# Create a startup script
RUN echo '#!/bin/bash\n\
flask db upgrade\n\
python app.py --host=0.0.0.0 --port=5000' > /app/start.sh && \
chmod +x /app/start.sh

CMD ["/app/start.sh"]
