from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connection
from faker import Faker

from comments.models import Comment
from content_entities.models import Blog, Topic

fake = Faker()


class Command(BaseCommand):
    tree_comments_count = 0
    current_level = 0

    username = 'super_admin'
    email = 'super_admin@admin.ru'
    password = 'hardP@ssw0rd'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='Delete all content',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_comments()
            self.clear_content()
        else:
            self.create_user()
            for _ in range(1):
                Blog.objects.create(title=fake.text().split('.')[0])
                Topic.objects.create(title=fake.text().split('.')[0])

            user = User.objects.get(username=self.username)
            self.generate_comments(Blog, user)
            self.generate_comments(Topic, user)

    def create_user(self):
        if User.objects.filter(username=self.username).exists():
            self.stdout.write('User creation skipped.')
        else:
            User.objects.create_superuser(self.username, self.email, self.password)
            self.stdout.write('User created')

    @staticmethod
    def clear_comments():
        with connection.cursor() as cursor:
            cursor.execute("delete from comments_comment;")

    @staticmethod
    def clear_content():
        Blog.objects.all().delete()
        Topic.objects.all().delete()

    def generate_comments(self, model, user):
        for obj in model.objects.all():
            self.create_first_level_comments(obj, user)

    def create_first_level_comments(self, obj, user):
        self.tree_comments_count = 0
        for _ in range(10):
            comment = Comment.objects.create(
                user=user,
                object_id=obj.id,
                content_type=obj.get_content_type(),
                text=fake.text().split('.')[0]
            )
            self.current_level = 0
            self.create_descendants_comments(comment, user)

    def create_descendants_comments(self, parent, user):
        for _ in range(3):
            if self.tree_comments_count < (10 ** 4) and self.current_level < 100:
                comment = Comment.objects.create(
                    parent=parent,
                    user=user,
                    object_id=parent.id,
                    content_type=parent.get_content_type(),
                    text=fake.text().split('.')[0]
                )
                self.tree_comments_count += 1
                self.current_level += 1
                self.create_descendants_comments(comment, user)
                self.current_level -= 1
