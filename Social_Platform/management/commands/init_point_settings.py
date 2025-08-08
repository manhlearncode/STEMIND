from django.core.management.base import BaseCommand
from Social_Platform.models import PointSettings

class Command(BaseCommand):
    help = 'Initialize default point settings'

    def handle(self, *args, **options):
        # Tạo hoặc cập nhật point settings với các giá trị mặc định
        settings, created = PointSettings.objects.get_or_create(id=1)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created default point settings')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Point settings already exist')
            )
            
        self.stdout.write(f'Current settings:')
        self.stdout.write(f'  - Create post: {settings.create_post_points} points')
        self.stdout.write(f'  - Like post: {settings.like_post_points} points')
        self.stdout.write(f'  - Share post: {settings.share_post_points} points')
        self.stdout.write(f'  - Comment: {settings.comment_points} points')
        self.stdout.write(f'  - Follow user: {settings.follow_user_points} points')
        self.stdout.write(f'  - Upload file: {settings.upload_file_points} points')
        self.stdout.write(f'  - Daily login: {settings.daily_login_points} points')
