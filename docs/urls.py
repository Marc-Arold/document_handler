from django.urls import path
from . import views

# app_name = 'documents_handler' 

urlpatterns = [
    path('error/', views.get_error_page, name='error_page'),
    path('', views.UploadDocumentView.as_view(), name='upload_document'),
    path('documents/', views.DocumentListView.as_view(), name='document_list'),
    path('split/<int:document_id>/', views.split_document, name='split_document'),
    path('embed/<int:document_id>/', views.create_embedding, name='create_embedding'),
]
