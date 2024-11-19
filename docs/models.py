from django.db import models
import jsonfield
from sqlalchemy import true

# Model to represent an uploaded document
class Document(models.Model):
    name = models.CharField(max_length=255)
    annee = models.CharField(max_length=255, null=True)
    type_loi = models.CharField(max_length=255,null=True)
    file = models.FileField(upload_to='documents/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Model to represent a split part of a document
class DocumentSplit(models.Model):
    document = models.ForeignKey(Document, related_name='splits', on_delete=models.CASCADE)
    # name = models.CharField(max_length=255)
    content = models.TextField(null=true)
    start_page = models.IntegerField()
    end_page = models.IntegerField()

    def __str__(self):
        return self.document.name

# Model to represent the embedding generated via OpenAI LLM (Se mwen te eseye fe me mpa kwe lap bon paske li pap two fit pou sa pito nou se on service spesyalize)
class DocumentEmbedding(models.Model):
    document_split = models.OneToOneField(DocumentSplit, related_name='embedding', on_delete=models.CASCADE)
    embedding_data = jsonfield.JSONField()

    def __str__(self):
        return f"Embedding for {self.document_split.name}"

