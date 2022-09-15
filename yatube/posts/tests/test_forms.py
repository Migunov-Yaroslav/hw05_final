import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTest(TestCase):
    """Класс предназначен тестирования форм приложения posts."""

    @classmethod
    def setUpClass(cls):
        """Создать объекты пользователя, группы и поста для тестовой БД."""
        super().setUpClass()
        cls.user = User.objects.create(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-group-2',
            description='Описание тестовой группы 2',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        # у another_gif отличается 5 и 7 байты
        cls.another_image = (
            b'\x47\x49\x46\x38\x37\x61\x01\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.another_uploaded = SimpleUploadedFile(
            name='another_image.gif',
            content=cls.another_image,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        """Удалить временную директорию MEDIA"""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создать авторизованный клиент."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """
        Проверить создание нового поста при отправке валидной формы на странице
        create_posts. Должно увеличиваться количество постов в БД, атрибуты
        нового поста должны совпадать с атрибутами, переданными в POST запросе.
        """
        posts_in_db_before = Post.objects.all()
        posts_count_in_db = len(posts_in_db_before)
        form_data = {
            'text': 'Новый пост от старого автора',
            'group': self.group.id,
            'image': self.uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        posts_in_db_after = Post.objects.all()
        target_post = set(posts_in_db_after) - set(posts_in_db_before)

        self.assertEqual(len(target_post), 1)

        post = target_post.pop()

        self.assertEqual(Post.objects.count(), posts_count_in_db + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image, 'posts/' + self.uploaded.name)

    def test_edit_post(self):
        """
        Проверить, что при редактировании поста изменяется соответствующий
        пост в БД (текст, группа и изображение, а автор остается неизменным)
        и не создается новый пост.
        """
        posts_count_in_db = Post.objects.count()
        form_data = {
            'text': 'Отредактированный старый пост',
            'group': self.group_2.id,
            'image': self.another_uploaded,
        }
        posts_author_before_change = self.post.author
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.post.refresh_from_db()

        self.assertEqual(posts_count_in_db, Post.objects.count())
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.group.id, form_data['group'])
        self.assertEqual(self.post.author, posts_author_before_change)
        self.assertEqual(
            self.post.image, 'posts/' + self.another_uploaded.name)

    def test_correct_show_new_comment(self):
        """
        Проверить, что после успешной отправки комментарий появляется на
        странице поста.
        """
        comments_in_db_before = Comment.objects.all()
        comments_count_in_db = len(comments_in_db_before)
        form_data = {
            'text': 'Новый комментарий',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        comments_in_db_after = Comment.objects.all()
        target_comment = set(comments_in_db_after) - set(comments_in_db_before)

        self.assertEqual(len(target_comment), 1)

        comment = target_comment.pop()

        self.assertEqual(Comment.objects.count(), comments_count_in_db + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post.id, self.post.id)
