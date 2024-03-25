from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from digestapi.models import Review, Book
from .books import BookSerializer


class ReviewSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        # Check if the user is the owner of the review
        return self.context["request"].user == obj.user

    book = BookSerializer(many=False)

    class Meta:
        model = Review
        fields = ["id", "book", "user", "rating", "comment", "date", "is_owner"]
        read_only_fields = ["user"]


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        # Get all reviews
        reviews = Review.objects.all()

        # Serialize the objects, and pass request to determine owner
        serializer = ReviewSerializer(reviews, many=True, context={"request": request})

        # Return the serialized data with 200 status code
        return Response(serializer.data)

    def create(self, request):
        # Create a new instance of a review and assign property
        book_id = request.data.get("book_id")
        book = Book.objects.get(pk=book_id)
        user = request.user

        new_review = Review.objects.create(
            # values from the request payload using `request.data`
            book=book,
            user=user,
            rating=request.data.get("rating"),
            comment=request.data.get("comment"),
        )

        # Save the review
        new_review.save()

        try:
            # Serialize the objects, and pass request as context
            serialized_review = ReviewSerializer(
                new_review, context={"request": request}
            )

            return Response(serialized_review.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            error_message = str(ex)
            data = {"message": error_message}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            # Get the requested review
            review = Review.objects.get(pk=pk)
            # Serialize the object (make sure to pass the request as context)
            serialized = ReviewSerializer(
                review, many=False, context={"request": request}
            )
            # Return the review with 200 status code
            return Response(serialized.data, status=status.HTTP_200_OK)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            # Get the requested review
            review = Review.objects.get(pk=pk)

            # Check if the user has permission to delete
            self.check_object_permissions(request, review)

            # Will return 403 if authenticated user is not author
            if review.user.id != request.user.id:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Delete the review
            review.delete()

            # Return success but no body
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
