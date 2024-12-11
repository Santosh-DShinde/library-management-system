from django.db import models
from ..model.base import Base

class Books(Base):
    title = models.CharField(max_length=155, unique=False, null=True, blank=True)
    author = models.CharField(max_length=155, unique=False, null=True, blank=True)

    class Meta:
        db_table = "books"

    def __str__(self):
        return str(self.pk)


