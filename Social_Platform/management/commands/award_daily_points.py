from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from Social_Platform.models import CustomUser
from Social_Platform.services.point_service import PointService


class Command(BaseCommand):
    help = 'Award daily points to active users'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days-back',
            type=int,
            default=0,
            help='Number of days back to check for login activity (default: 0 for today only)',
        )
    
    def handle(self, *args, **options):
        days_back = options['days_back']
        target_date = date.today() - timedelta(days=days_back)
        
        self.stdout.write(f'Awarding daily points for {target_date}...')
        
        # Lấy tất cả users đã login trong ngày
        # Có thể customize logic này dựa trên last_login hoặc activity log
        users = CustomUser.objects.filter(
            last_login__date=target_date
        ).distinct()
        
        awarded_count = 0
        skipped_count = 0
        
        for user in users:
            success, message = PointService.check_and_award_daily_points(user)
            
            if success:
                awarded_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {user.username}: {message}')
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'- {user.username}: {message}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Awarded: {awarded_count}, Skipped: {skipped_count}'
            )
        )
