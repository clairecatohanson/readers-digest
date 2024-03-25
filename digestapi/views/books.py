from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.response import Response
from digestapi.models import Book
from .categories import CategorySerializer


class BookSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True)

    def get_is_owner(self, obj):
        # Check if authenticated user is owner
        return self.context["request"].user == obj.user

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "cover_url",
            "is_owner",
            "categories",
        ]


class BookViewSet(viewsets.ViewSet):
    def list(self, request):
        books = Book.objects.all()
        serialized = BookSerializer(books, many=True, context={"request": request})
        return Response(serialized.data)

    def retrieve(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
            serialized = BookSerializer(book, many=False, context={"request": request})
            return Response(serialized.data)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # Get the data from the client's JSON payload
        title = request.data.get("title")
        author = request.data.get("author")
        isbn = request.data.get("isbn")
        cover_url = request.data.get("cover_url")

        # Create a book database row first, so you have a primary key to work with
        book = Book.objects.create(
            user=request.user,
            title=title,
            author=author,
            isbn=isbn,
            cover_url=cover_url,
        )

        # Establish the many-to-many relationships
        category_ids = request.data.get("categories", [])
        book.categories.set(category_ids)

        serializer = BookSerializer(book, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
            # Is teh authenticated user allowed to edit this book?
            self.check_object_permissions(request, book)

            serializer = BookSerializer(data=request.data, many=False)
            if serializer.is_valid():
                book.title = serializer.validated_data["title"]
                book.author = serializer.validated_data["author"]
                book.isbn = serializer.validated_data["isbn"]
                book.cover_url = serializer.validated_data["cover_url"]
                book.save()

                category_objects = request.data.get("categories", [])
                category_ids = [category["id"] for category in category_objects]
                book.categories.set(category_ids)

                serializer = BookSerializer(book, context={"request": request})
                return Response(None, status.HTTP_204_NO_CONTENT)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
            self.check_object_permissions(request, book)
            book.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
