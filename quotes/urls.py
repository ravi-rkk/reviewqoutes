"""
URL routing for the quotes app.
This file maps URLs to view classes, defining our API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuoteViewSet, QuoteReportView, BookViewSet, ReviewViewSet,
    # Template views
    home, quote_list, quote_detail, quote_create, quote_edit, quote_delete, quote_fetch_bio,
    book_list, book_detail, book_create, book_edit, book_delete,
    review_create, review_edit, review_delete
)

# DefaultRouter automatically creates RESTful URLs for our ViewSets
# It handles things like /api/quotes/, /api/quotes/{id}/, etc.
router = DefaultRouter()

# Register our ViewSets with the router
# This automatically creates all CRUD endpoints for each model
router.register(r'quotes', QuoteViewSet)      # Creates /api/quotes/ endpoints
router.register(r'books', BookViewSet)         # Creates /api/books/ endpoints
router.register(r'reviews', ReviewViewSet)     # Creates /api/reviews/ endpoints

urlpatterns = [
    # Include all the router-generated URLs
    # This includes all the CRUD endpoints for quotes, books, and reviews
    path('', include(router.urls)),
    
    # Custom endpoint for reporting/visualization data
    # This is a simple APIView, not a ViewSet, so we define it separately
    path('reporting-quote-counts/', QuoteReportView.as_view(), name='quote-report-counts'),
]

# Template URLs (for MVT pattern)
template_urlpatterns = [
    # Quotes
    path('quotes/', quote_list, name='quote_list'),
    path('quotes/<int:pk>/', quote_detail, name='quote_detail'),
    path('quotes/create/', quote_create, name='quote_create'),
    path('quotes/<int:pk>/edit/', quote_edit, name='quote_edit'),
    path('quotes/<int:pk>/delete/', quote_delete, name='quote_delete'),
    path('quotes/<int:pk>/fetch-bio/', quote_fetch_bio, name='quote_fetch_bio'),
    
    # Books
    path('books/', book_list, name='book_list'),
    path('books/<int:pk>/', book_detail, name='book_detail'),
    path('books/create/', book_create, name='book_create'),
    path('books/<int:pk>/edit/', book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', book_delete, name='book_delete'),
    
    # Reviews
    path('books/<int:book_id>/reviews/create/', review_create, name='review_create'),
    path('reviews/<int:pk>/edit/', review_edit, name='review_edit'),
    path('reviews/<int:pk>/delete/', review_delete, name='review_delete'),
]