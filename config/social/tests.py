from django.test import TestCase

import pytest
from django.utils import timezone
from users.models import User
from social.models import Post, Comment, Like, Share

@pytest.mark.django_db
def test_create_post():
    user = User.objects.create_user(username="tester", password="pass123")
    post = Post.objects.create(author=user, content="Hello World!")

    assert post.content == "Hello World!"
    assert post.author == user
    assert post.created_at.date() == timezone.now().date()
    assert post.popularity_score == 0  # no likes/comments/shares yet


@pytest.mark.django_db
def test_like_comment_share_counts():
    user = User.objects.create_user(username="tester", password="pass123")
    other = User.objects.create_user(username="friend", password="pass123")
    post = Post.objects.create(author=user, content="Test Post")

    # Add like
    Like.objects.create(post=post, user=other)
    # Add comment
    Comment.objects.create(post=post, user=other, text="Nice post!")
    # Add share
    Share.objects.create(post=post, user=other)

    post.refresh_from_db()

    assert post.likes_count == 1
    assert post.comments_count == 1
    assert post.shares_count == 1
    assert post.popularity_score == (1*1) + (1*2) + (1*3)  # = 6


@pytest.mark.django_db
def test_unique_like_constraint():
    user = User.objects.create_user(username="tester", password="pass123")
    post = Post.objects.create(author=user, content="Duplicate Like Test")

    Like.objects.create(post=post, user=user)
    with pytest.raises(Exception):  # IntegrityError
        Like.objects.create(post=post, user=user)


@pytest.mark.django_db
def test_unique_share_constraint():
    user = User.objects.create_user(username="tester", password="pass123")
    post = Post.objects.create(author=user, content="Duplicate Share Test")

    Share.objects.create(post=post, user=user)
    with pytest.raises(Exception):  # IntegrityError
        Share.objects.create(post=post, user=user)
