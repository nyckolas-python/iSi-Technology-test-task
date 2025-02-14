from django.core.management.base import BaseCommand
from django.core.management import call_command
from datetime import datetime
import os


class Command(BaseCommand):
    help = 'Create database dump'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default=None,
            help='Output file path'
        )

    def handle(self, *args, **options):
        output = options['output']
        if not output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output = f'db_dump_{timestamp}.json'

        # Ensure dumps directory exists
        dumps_dir = 'dumps'
        if not os.path.exists(dumps_dir):
            os.makedirs(dumps_dir)

        output_path = os.path.join(dumps_dir, output)

        self.stdout.write(f'Creating database dump to {output_path}...')

        # Create dump
        with open(output_path, 'w') as f:
            call_command('dumpdata', 
                        'auth.user', 
                        'threads.thread', 
                        'threads.message',
                        indent=2,
                        stdout=f)

        self.stdout.write(self.style.SUCCESS(f'Database dump created successfully at {output_path}')) 