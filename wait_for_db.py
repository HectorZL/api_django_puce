import os
import time
import psycopg2
from django.db import connections
from django.db.utils import OperationalError

def wait_for_db():
    """Wait for the database to be available."""
    print('Waiting for database...')
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                dbname=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                host=os.environ.get('DB_HOST'),
                port=os.environ.get('DB_PORT')
            )
            conn.close()
            print('Database is available!')
            return True
        except psycopg2.OperationalError as e:
            retry_count += 1
            print(f'Database not ready, retrying... ({retry_count}/{max_retries})')
            time.sleep(1)
    
    print('Max retries reached. Database is not available.')
    return False

if __name__ == '__main__':
    wait_for_db()
