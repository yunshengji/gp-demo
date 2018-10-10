import datetime
from demo.model.article import Article


def save_new_article(data):
    data['title'] = data['title'].strip()
    data['author'] = data['author'].strip()
    article = Article(**data).save()
    return article
    raise Exception("Failed to save this article")


def update_article(data, article):
        article.title = data['title'].strip()
        article.author = data.get('author', article.author)
        article.updated = datetime.datetime.now()
        return article.save()
