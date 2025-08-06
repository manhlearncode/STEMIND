from django.core.management.base import BaseCommand
from File_sharing_platform.models import Category


class Command(BaseCommand):
    help = 'Tạo 4 parent categories với child categories'

    def handle(self, *args, **options):
        # Xóa tất cả categories hiện tại
        Category.objects.all().delete()
        self.stdout.write('Đã xóa tất cả categories cũ')

        # Tạo 4 parent categories
        parent_categories = {
            'Theo lĩnh vực': [
                'Toán học',
                'Vật lý', 
                'Hóa học',
                'Sinh học',
                'Công nghệ thông tin'
            ],
            'Theo đối tượng': [
                'Lớp 1',
                'Lớp 2',
                'Lớp 3', 
                'Lớp 4',
                'Lớp 5',
                'Lớp 6',
                'Lớp 7',
                'Lớp 8',
                'Lớp 9',
                'Lớp 10',
                'Lớp 11',
                'Lớp 12'
            ],
            'Theo loại tài liệu': [
                'Bài giảng',
                'Bài tập',
                'Đề thi',
                'Tài liệu tham khảo',
                'Sách giáo khoa',
                'Giáo án'
            ],
            'Theo cấp độ': [
                'Cơ bản',
                'Trung bình',
                'Nâng cao',
                'Chuyên sâu'
            ]
        }

        # Tạo parent categories và child categories
        for parent_name, child_names in parent_categories.items():
            parent = Category.objects.create(
                name=parent_name,
                description=f'Danh mục {parent_name.lower()}'
            )
            self.stdout.write(f'Đã tạo parent category: {parent_name}')
            
            for child_name in child_names:
                child = Category.objects.create(
                    name=child_name,
                    parent=parent,
                    description=f'{child_name} thuộc {parent_name}'
                )
                self.stdout.write(f'  └ Đã tạo child category: {child_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Hoàn thành! Đã tạo {len(parent_categories)} parent categories và {sum(len(children) for children in parent_categories.values())} child categories'
            )
        ) 