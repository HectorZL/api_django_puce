import time
from django.core.management.base import BaseCommand
import psycopg2
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        """Handle the command"""
        self.stdout.write('Waiting for database...')
        db_conn = None
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                conn = psycopg2.connect(
                    dbname='catering_db',
                    user='postgres',
                    password='postgres',
                    host='db',
                    port='5432'
                )
                conn.close()
                self.stdout.write(self.style.SUCCESS('Database is available!'))
                return
            except psycopg2.OperationalError as e:
                retry_count += 1
                self.stdout.write(f'Database not ready, retrying... ({retry_count}/{max_retries})')
                time.sleep(1)
        
        self.stdout.write(self.style.ERROR('Max retries reached. Database is not available.'))
