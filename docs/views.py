from django.shortcuts import render

# Create your views here.
from cgitb import text
from django.shortcuts import render
from qdrant_client import QdrantClient
from langchain.vectorstores.pgvector import PGVector
from django.http import JsonResponse
# Create your views here.
from django.shortcuts import render, redirect
from .models import Document, DocumentSplit, DocumentEmbedding
from .forms import DocumentForm
from langchain_community.document_loaders import DataFrameLoader
from .qgrantinit import qdrant_client
from django.views import View
import openai 
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
# import pinecone 
from tqdm.auto import tqdm
from langchain_community.vectorstores import Qdrant
from dotenv import load_dotenv
from environ import Env

load_dotenv()
env = Env()
Env.read_env()

API_KEY=env('API_KEY')
QDRAT_API_KEY=env('QDRAT_API_KEY')
url=env('url')
# Placeholder function to simulate OpenAI LLM embedding

# def is_superuser(user):
#     return user.is_superuser

def generate_embedding(texts):
    EMBEDDING = OpenAIEmbeddings(openai_api_key=API_KEY)
    res = EMBEDDING.embed_documents(texts)
    return res

class UploadDocumentView(View):
    def get(self, request):
        form = DocumentForm()
        return render(request, 'document_handler/upload.html', {'form': form})

    def post(self, request):
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('document_list')

class DocumentListView(View):
    def get(self, request):
        documents = Document.objects.all()
        return render(request, 'document_handler/document_list.html', {'documents': documents})

# @login_required
# @user_passes_test(is_superuser)
def split_document(request, document_id):
    document = Document.objects.get(id=document_id)
    document_path = document.file.path
    loader = PyPDFLoader(document_path)
    pages = loader.load()
    
    TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    DOCS = TEXT_SPLITTER.split_documents(pages)

  
    for doc in DOCS:
        DocumentSplit.objects.create(
            document=document,
            content = doc.page_content,
            start_page=doc.metadata['page'],
            end_page=doc.metadata['page']  # Assuming len(doc) provides meaningful information
        )

    return redirect('document_list')
import re

from qdrant_client.http import models
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
import pandas as pd
import uuid


def create_embedding(request, document_id):
    # Récupération du document et de ses splits
    related_splits = DocumentSplit.objects.filter(document=document_id)
    if not related_splits.exists():
        return JsonResponse({'error': 'Document non trouvé ou sans splits associés'}, status=404)
    
    # Récupération des informations du document
    document = related_splits.first().document
    annee_doc = document.annee
    type_loi = document.type_loi

    # Préparation des données pour la création des embeddings
    texts = [split.content for split in related_splits]
    payloads = [{'annee': annee_doc, 'type_loi': type_loi} for _ in range(len(texts))]
    df = pd.DataFrame(list(zip(texts, payloads)),
               columns =['texts', 'payloads'])
    loader = DataFrameLoader(df, page_content_column="texts")
    client_open_ai = OpenAI(organization='org-HzJAqf3j5XzlrzcOni4246am', api_key=API_KEY)

    documents = loader.load()
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=API_KEY)
    qdrant = Qdrant.from_documents(
    documents=documents,
    embedding=embeddings,
    url=url,
    collection_name="haitian_law",
    api_key=QDRAT_API_KEY
    )
    
    return JsonResponse({'message': 'Embeddings créés et stockés avec succès'})

def get_error_page(request):
        return render(request, 'error.html')

