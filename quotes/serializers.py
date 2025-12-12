
"""
Serializers convert Django model instances to JSON and vice versa.
They also handle validation and can add computed fields.
"""

from rest_framework import serializers
from .models import Quote, Book, Review


class QuoteSerializer(serializers.ModelSerializer):
    """
    Serializer for Quote model.
    Handles converting quotes to/from JSON format for API responses.
    Includes all fields from the Quote model.
    """
    class Meta:
        model = Quote
        fields = '__all__'  # Include all fields: text, author, era, author_bio_summary, date_created


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    Handles review data when creating, reading, or updating reviews.
    The 'book' field is important - it's the ID of the book being reviewed.
    """
    class Meta:
        model = Review
        # Only include these specific fields in the API
        # We don't want to expose internal Django fields
        fields = ['id', 'book', 'reviewer_name', 'rating', 'body', 'created_at']
        
        # Note: 'book' field is necessary because when creating a review,
        # the frontend sends the book ID, and we need to link the review to that book


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model.
    Includes a computed field for the full image URL and nested reviews.
    """
    # When fetching a book, we can optionally include all its reviews
    # This is read-only - you can't create reviews through this field
    reviews = ReviewSerializer(many=True, read_only=True) 
    
    # Computed field that returns the full URL to the book cover image
    # This is helpful for the frontend - it gets the complete URL ready to use
    cover_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover_image', 'cover_image_url', 'reviews']
    
    def get_cover_image_url(self, obj):
        """
        Computes the full URL for the book cover image.
        If there's a request context (which there should be), it builds
        an absolute URL like: http://localhost:8000/media/book_covers/image.jpg
        Otherwise, it just returns the relative path.
        """
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                # Build full URL including domain and port
                return request.build_absolute_uri(obj.cover_image.url)
            # Fallback to relative URL if no request context
            return obj.cover_image.url
        return None  # No image uploaded