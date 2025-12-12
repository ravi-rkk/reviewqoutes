"""
API views for handling HTTP requests.
This file contains all the view classes that handle CRUD operations
and custom actions like fetching Wikipedia data.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count 
from django.contrib import messages
import requests

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

# Import our models and serializers
from .models import Quote, Book, Review 
from .serializers import QuoteSerializer, BookSerializer, ReviewSerializer


# Wikipedia API endpoint - we'll use this to fetch author biographies
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


# =========================================================
# 1. QUOTE CRUD VIEW SET
# =========================================================

class QuoteViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD operations for quotes.
    Django REST Framework automatically creates endpoints for:
    - GET /api/quotes/ (list all quotes)
    - POST /api/quotes/ (create new quote)
    - GET /api/quotes/{id}/ (get specific quote)
    - PUT /api/quotes/{id}/ (update quote)
    - DELETE /api/quotes/{id}/ (delete quote)
    """
    # All quotes in the database
    queryset = Quote.objects.all()
    
    # Serializer handles converting between Python objects and JSON
    serializer_class = QuoteSerializer

    @action(detail=True, methods=['post'], url_path='fetch-bio')
    def fetch_author_bio(self, request, pk=None):
        """
        Custom action to fetch author biography from Wikipedia.
        This is called via POST /api/quotes/{id}/fetch-bio/
        
        It's a cool feature - when you have a quote, you can fetch
        the author's bio from Wikipedia and save it to the database.
        """
        # First, make sure the quote exists
        try:
            quote = self.get_object()
        except Quote.DoesNotExist:
            return Response({"error": "Quote not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the author's name from the quote
        author_name = quote.author
        
        # Prepare parameters for Wikipedia API request
        # We're asking for a brief intro extract in plain text format
        params = {
            "action": "query",           # Standard Wikipedia API action
            "format": "json",            # We want JSON response
            "titles": author_name,       # Search for this author
            "prop": "extracts",          # Get the article extract
            "exintro": True,             # Just the intro section (first paragraph)
            "explaintext": True,         # Plain text, no HTML
            "redirects": 1               # Follow redirects if author name is slightly different
        }
        
        try:
            # Wikipedia requires a User-Agent header to identify the application
            headers = {
                'User-Agent': 'PoetsCanvas/1.0 (https://github.com/yourusername/poets-canvas; contact@example.com)'
            }
            # Make the request to Wikipedia with a 5 second timeout
            # We don't want to wait forever if Wikipedia is slow
            response = requests.get(WIKIPEDIA_API_URL, params=params, headers=headers, timeout=5) 
            response.raise_for_status()  # Raise an error if request failed
            
            # Parse the JSON response
            data = response.json()
            
            # Check if we got any pages
            if 'query' not in data or 'pages' not in data['query'] or not data['query']['pages']:
                return Response(
                    {"error": f"No Wikipedia article found for {author_name}."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Wikipedia returns pages in a dict, we just need the first (and usually only) page
            page = next(iter(data['query']['pages'].values()))
            
            # Check if page exists (Wikipedia returns -1 for missing pages)
            if 'missing' in page or page.get('pageid', -1) == -1:
                return Response(
                    {"error": f"No Wikipedia article found for {author_name}."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            summary = page.get('extract', 'No summary found.')
            
            if not summary or summary == 'No summary found.':
                return Response(
                    {"error": f"Wikipedia article found but no summary available for {author_name}."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Save the biography to our database
            # This way we don't have to fetch it every time
            quote.author_bio_summary = summary
            quote.save()
            
            # Return success response with the fetched bio
            return Response(
                {"message": f"Successfully fetched and saved bio for {author_name}.", "summary": summary},
                status=status.HTTP_200_OK
            )
            
        except requests.RequestException as e:
            # If something went wrong (network error, timeout, etc.)
            # Return a proper error response
            return Response(
                {"error": f"External API error while fetching bio: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


# =========================================================
# 2. REPORTING API VIEW
# =========================================================

class QuoteReportView(APIView):
    """
    Special endpoint for generating report data.
    This aggregates quotes by their literary era and counts them.
    The frontend uses this data to create beautiful charts and visualizations.
    
    Example response:
    [
        {"era": "Romantic", "quote_count": 15},
        {"era": "Modern", "quote_count": 8},
        ...
    ]
    """
    def get(self, request, format=None):
        """
        GET /api/reporting-quote-counts/
        
        Groups all quotes by era and counts how many quotes are in each era.
        Returns the results sorted by count (highest first).
        """
        # Group quotes by era and count them
        # This is a Django ORM aggregation - very efficient!
        report_data = Quote.objects.values('era').annotate(
            quote_count=Count('id')
        ).order_by('-quote_count')  # Order by count descending
        
        # Convert QuerySet to list so we can return it as JSON
        report_list = list(report_data)
        
        return Response(report_list, status=status.HTTP_200_OK)


# =========================================================
# 3. BOOK CRUD VIEW SET
# =========================================================

class BookViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD operations for books.
    Books are used when creating reviews - users can select a book
    or create a new one with a cover image.
    """
    # Get all books, ordered alphabetically by title
    queryset = Book.objects.all().order_by('title')
    serializer_class = BookSerializer
    
    def get_serializer_context(self):
        """
        Pass the request object to the serializer.
        This is needed so the serializer can build absolute URLs
        for book cover images (like http://localhost:8000/media/book_covers/image.jpg)
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# =========================================================
# 4. REVIEW CRUD VIEW SET
# =========================================================

class ReviewViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD operations for book reviews.
    Users can create, read, update, and delete reviews.
    Reviews are ordered by creation date (newest first).
    """
    # Get all reviews, newest first
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        """
        Allows filtering reviews by book_id via query parameter.
        Example: GET /api/reviews/?book_id=5
        This returns only reviews for book with ID 5.
        """
        queryset = super().get_queryset()
        book_id = self.request.query_params.get('book_id')
        
        # If book_id is provided, filter reviews for that book
        if book_id is not None:
            queryset = queryset.filter(book_id=book_id)
        
        return queryset


# =========================================================
# 5. TEMPLATE VIEWS (MVT Pattern)
# =========================================================

def home(request):
    """Home page view showing recent quotes and navigation."""
    recent_quotes = Quote.objects.all().order_by('-date_created')[:5]
    return render(request, 'quotes/home.html', {'recent_quotes': recent_quotes})


# Quote Template Views
def quote_list(request):
    """List all quotes."""
    quotes = Quote.objects.all().order_by('-date_created')
    return render(request, 'quotes/quote_list.html', {'quotes': quotes})


def quote_detail(request, pk):
    """Show details of a specific quote."""
    quote = get_object_or_404(Quote, pk=pk)
    return render(request, 'quotes/quote_detail.html', {'quote': quote})


def quote_create(request):
    """Create a new quote."""
    if request.method == 'POST':
        text = request.POST.get('text')
        author = request.POST.get('author')
        era = request.POST.get('era', '')
        
        if text and author:
            quote = Quote.objects.create(text=text, author=author, era=era if era else None)
            messages.success(request, 'Quote created successfully!')
            return redirect('quote_detail', pk=quote.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'quotes/quote_form.html')


def quote_edit(request, pk):
    """Edit an existing quote."""
    quote = get_object_or_404(Quote, pk=pk)
    
    if request.method == 'POST':
        quote.text = request.POST.get('text')
        quote.author = request.POST.get('author')
        quote.era = request.POST.get('era', '') or None
        quote.save()
        messages.success(request, 'Quote updated successfully!')
        return redirect('quote_detail', pk=quote.id)
    
    return render(request, 'quotes/quote_form.html', {'quote': quote})


def quote_delete(request, pk):
    """Delete a quote."""
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        quote.delete()
        messages.success(request, 'Quote deleted successfully!')
        return redirect('quote_list')
    return redirect('quote_detail', pk=pk)


def quote_fetch_bio(request, pk):
    """Fetch author bio from Wikipedia for a quote."""
    quote = get_object_or_404(Quote, pk=pk)
    
    if request.method == 'POST':
        author_name = quote.author
        
        params = {
            "action": "query",
            "format": "json",
            "titles": author_name,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "redirects": 1
        }
        
        try:
            # Wikipedia requires a User-Agent header to identify the application
            headers = {
                'User-Agent': 'PoetsCanvas/1.0 (https://github.com/yourusername/poets-canvas; contact@example.com)'
            }
            response = requests.get(WIKIPEDIA_API_URL, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Check if we got any pages
            if 'query' not in data or 'pages' not in data['query'] or not data['query']['pages']:
                messages.error(request, f'No Wikipedia article found for {author_name}.')
                return redirect('quote_detail', pk=pk)
            
            page = next(iter(data['query']['pages'].values()))
            
            # Check if page exists (Wikipedia returns -1 for missing pages)
            if 'missing' in page or page.get('pageid', -1) == -1:
                messages.error(request, f'No Wikipedia article found for {author_name}.')
                return redirect('quote_detail', pk=pk)
            
            summary = page.get('extract', 'No summary found.')
            
            if not summary or summary == 'No summary found.':
                messages.error(request, f'Wikipedia article found but no summary available for {author_name}.')
                return redirect('quote_detail', pk=pk)
            
            quote.author_bio_summary = summary
            quote.save()
            messages.success(request, f'Successfully fetched bio for {author_name}!')
        except requests.RequestException as e:
            messages.error(request, f'Error fetching bio: {str(e)}')
    
    return redirect('quote_detail', pk=pk)


# Book Template Views
def book_list(request):
    """List all books."""
    books = Book.objects.all().order_by('title')
    return render(request, 'quotes/book_list.html', {'books': books})


def book_detail(request, pk):
    """Show details of a specific book with its reviews."""
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all().order_by('-created_at')
    return render(request, 'quotes/book_detail.html', {'book': book, 'reviews': reviews})


def book_create(request):
    """Create a new book."""
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        cover_image = request.FILES.get('cover_image')
        
        if title and author:
            book = Book.objects.create(title=title, author=author)
            if cover_image:
                book.cover_image = cover_image
                book.save()
            messages.success(request, 'Book created successfully!')
            return redirect('book_detail', pk=book.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'quotes/book_form.html')


def book_edit(request, pk):
    """Edit an existing book."""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        cover_image = request.FILES.get('cover_image')
        
        if cover_image:
            book.cover_image = cover_image
        
        book.save()
        messages.success(request, 'Book updated successfully!')
        return redirect('book_detail', pk=book.id)
    
    return render(request, 'quotes/book_form.html', {'book': book})


def book_delete(request, pk):
    """Delete a book."""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')
    return redirect('book_detail', pk=pk)


# Review Template Views
def review_create(request, book_id):
    """Create a new review for a book."""
    book = get_object_or_404(Book, pk=book_id)
    
    if request.method == 'POST':
        reviewer_name = request.POST.get('reviewer_name')
        rating = request.POST.get('rating')
        body = request.POST.get('body')
        
        if reviewer_name and rating and body:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    review = Review.objects.create(
                        book=book,
                        reviewer_name=reviewer_name,
                        rating=rating,
                        body=body
                    )
                    messages.success(request, 'Review created successfully!')
                    return redirect('book_detail', pk=book.id)
                else:
                    messages.error(request, 'Rating must be between 1 and 5.')
            except ValueError:
                messages.error(request, 'Invalid rating value.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'quotes/review_form.html', {'book': book})


def review_edit(request, pk):
    """Edit an existing review."""
    review = get_object_or_404(Review, pk=pk)
    book = review.book
    
    if request.method == 'POST':
        review.reviewer_name = request.POST.get('reviewer_name')
        rating = request.POST.get('rating')
        review.body = request.POST.get('body')
        
        try:
            rating = int(rating)
            if 1 <= rating <= 5:
                review.rating = rating
                review.save()
                messages.success(request, 'Review updated successfully!')
                return redirect('book_detail', pk=book.id)
            else:
                messages.error(request, 'Rating must be between 1 and 5.')
        except ValueError:
            messages.error(request, 'Invalid rating value.')
    
    return render(request, 'quotes/review_form.html', {'book': book, 'review': review})


def review_delete(request, pk):
    """Delete a review."""
    review = get_object_or_404(Review, pk=pk)
    book = review.book
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('book_detail', pk=book.id)
    return redirect('book_detail', pk=book.id)