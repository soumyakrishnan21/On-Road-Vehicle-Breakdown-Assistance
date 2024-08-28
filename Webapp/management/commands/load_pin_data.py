# F:\Django_Projects\ORVBA\Webapp\management\commands\load_pin_data.py

from django.core.management.base import BaseCommand, CommandError
from Webapp.models import PINLocation  # Adjust the import based on your project structure
import csv


class Command(BaseCommand):
    help = 'Load PIN code data from CSV'

    def handle(self, *args, **options):
        file_path = 'C:\\Users\\SOUMYA\\Downloads\\pincode.csv'  # Adjust the file path as per your actual path
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header row

                for row in reader:
                    try:
                        latitude = float(row[4])
                        longitude = float(row[5])
                        pin_code = row[1].strip()  # Remove any leading/trailing whitespace
                        PINLocation.objects.create(latitude=latitude, longitude=longitude, pin_code=pin_code)
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f'Skipping row due to invalid data: {row}'))

            self.stdout.write(self.style.SUCCESS('Successfully loaded PIN code data'))

        except Exception as e:
            raise CommandError(f'Error loading data: {str(e)}')
