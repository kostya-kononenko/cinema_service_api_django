from rest_framework import serializers

from cinema.models import Movie, Reviews, Rating


class FilterReviewListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ("title", "tagline")


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Reviews
        fields = ("name", "text", "children")


class MovieDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    directors = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    actors = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ("draft", )


class CreateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("star", "movie")

        def create(self, validate_data):
            rating = Rating.objects.update_or_create(
                ip=validate_data.get("ip", None),
                movie=validate_data.get("movie", None),
                defaults={"star": validate_data.get("star")}
            )
            return rating
