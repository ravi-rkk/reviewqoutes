
"""
Database models for the Poet's Canvas application.
These models define the structure of our data - quotes, books, and reviews.
"""

from django.db import models


class Quote(models.Model):
    """
    Represents a quote or piece of poetry in our collection.
    Each quote has text, an author, and optionally an era classification.
    We can also store author biographies fetched from Wikipedia.
    """
    # The actual quote or poem text - can be long, so we use TextField
    text = models.TextField()
    
    # Author's name - keeping it simple with just a name field
    author = models.CharField(max_length=100)
    
    # Literary era (like "Romantic", "Modern", "Classical") - optional field
    # This helps us categorize and visualize quotes by time period
    era = models.CharField(max_length=50, blank=True, null=True)
    
    # This field stores author biography fetched from Wikipedia API
    # It's optional since we fetch it on-demand, not when creating a quote
    author_bio_summary = models.TextField(blank=True, null=True) 
    
    # Automatically set when the quote is first created
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a nice string representation for admin panel and debugging.
        Shows first 30 characters of the quote followed by author name.
        """
        return f'"{self.text[:30]}..." by {self.author}'


class Book(models.Model):
    """
    Represents a book in our collection.
    Users can upload book cover images when creating reviews.
    """
    # Book title - can be long, so we allow up to 255 characters
    title = models.CharField(max_length=255)
    
    # Author of the book
    author = models.CharField(max_length=255)
    
    # Book cover image - stored in 'book_covers/' directory
    # This is optional since not all books might have covers uploaded
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True) 

    def __str__(self):
        """
        Simple string representation - just the title.
        Makes it easy to identify books in admin panel.
        """
        return self.title


class Review(models.Model):
    """
    Represents a book review written by a user.
    Each review is linked to a specific book and includes rating and text.
    """
    # Links this review to a specific book
    # If the book is deleted, all its reviews are deleted too (CASCADE)
    # The 'related_name' lets us access reviews from a book: book.reviews.all()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews') 
    
    # Name of the person writing the review
    reviewer_name = models.CharField(max_length=100) 
    
    # Rating from 1 to 5 stars - defaults to 5 if not specified
    rating = models.IntegerField(default=5)
    
    # The actual review text - what the reviewer thought about the book
    body = models.TextField()

    # When the review was created - automatically set
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a descriptive string showing who reviewed which book.
        Helpful for admin panel and debugging.
        """
        return f"Review by {self.reviewer_name} for {self.book.title}"