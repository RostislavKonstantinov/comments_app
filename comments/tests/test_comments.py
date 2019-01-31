import random
import string

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from comments.models import Comment
from content_entities.models import Blog


def random_string():
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(20)])


class TestComments(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.first_user = User.objects.create_user(random_string())
        cls.second_user = User.objects.create_user(random_string())
        cls.entity = Blog.objects.create(title=random_string())
        for _ in range(10):
            parent = Comment.objects.create(
                user=random.choice([cls.first_user, cls.second_user]),
                object_id=cls.entity.id,
                content_type=cls.entity.get_content_type(),
                text=random_string()
            )
            for lvl in range(10):
                parent = Comment.objects.create(
                    user=random.choice([cls.first_user, cls.second_user]),
                    object_id=parent.id,
                    content_type=parent.get_content_type(),
                    text=random_string(),
                    parent=parent
                )
        super().setUpTestData()

    def test_list_by_user(self):
        response = self.client.get(reverse('comments-list'), data=dict(user=self.first_user.id)).json()
        self.assertEqual(
            len(response['results']),
            Comment.objects.filter(user=self.first_user.id).count()
        )

    def test_list_by_entity(self):
        data = dict(content_type=self.entity.self_content_type, object_id=self.entity.id)
        response = self.client.get(reverse('comments-list'), data=data).json()
        self.assertEqual(
            len(response['results']),
            Comment.objects.filter(**data).count()
        )

    def test_list_by_parent(self):
        comment = Comment.objects.filter(parent__isnull=True).first()
        data = dict(parent=comment.id)
        response = self.client.get(reverse('comments-list'), data=data).json()
        self.assertEqual(
            len(response['results']),
            comment.children.all().count()
        )

    def test_children_by_parent(self):
        comment = Comment.objects.filter(parent__isnull=True).first()
        data = dict(parent=comment.id, children='true')
        response = self.client.get(reverse('comments-list'), data=data).json()
        self.assertEqual(
            len(response),
            comment.get_descendant_count()
        )

    def test_children_by_entity(self):
        comment = Comment.objects.filter(parent__isnull=True).first()
        data = dict(content_type=comment.self_content_type, object_id=comment.id, children='true')
        response = self.client.get(reverse('comments-list'), data=data).json()
        self.assertEqual(
            len(response),
            comment.get_descendant_count()
        )
