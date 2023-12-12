from blog.models import Author


def is_author(user):
    try:
        Author.objects.get(user=user)
        return True
    except Author.DoesNotExist:
        return False
