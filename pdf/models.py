from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class Document(models.Model):
  docfile = models.FileField(upload_to="")