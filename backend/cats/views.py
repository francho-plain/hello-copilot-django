from datetime import timedelta
from typing import Any, Dict

from django.db import transaction
from django.db.models import Avg, Count, Max, Min, Q
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Cat
from .serializers import (AdoptCatSerializer, BreedStatisticsSerializer,
                          CatListSerializer, CatSerializer,
                          CatStatisticsSerializer)


class CatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Cat model providing full CRUD operations and additional actions.

    This ViewSet provides:
    - Standard CRUD operations (list, create, retrieve, update, destroy)
    - Search and filtering capabilities
    - Custom actions for adoption, statistics, and breed information
    """

    queryset = Cat.objects.all().order_by("id")
    serializer_class = CatSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "breed", "color", "description"]
    ordering_fields = ["id", "name", "age", "weight", "created_at"]
    ordering = ["id"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return CatListSerializer
        elif self.action == "adopt":
            return AdoptCatSerializer
        return CatSerializer

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = Cat.objects.all()

        # Filter by adoption status
        adoption_status = self.request.query_params.get("status", None)
        if adoption_status == "available":
            queryset = queryset.filter(adoption_date__isnull=True)
        elif adoption_status == "adopted":
            queryset = queryset.filter(adoption_date__isnull=False)

        # Filter by breed
        breed = self.request.query_params.get("breed", None)
        if breed:
            queryset = queryset.filter(breed__icontains=breed)

        # Filter by neutered status
        neutered = self.request.query_params.get("neutered", None)
        if neutered is not None:
            is_neutered = neutered.lower() in ["true", "1", "yes"]
            queryset = queryset.filter(is_neutered=is_neutered)

        # Filter by age range
        min_age = self.request.query_params.get("min_age", None)
        max_age = self.request.query_params.get("max_age", None)
        if min_age:
            queryset = queryset.filter(age__gte=min_age)
        if max_age:
            queryset = queryset.filter(age__lte=max_age)

        return queryset.order_by(self.ordering[0])

    def create(self, request: Request) -> Response:
        """
        Create a new cat with user-defined custom parameters.

        POST /api/cats/
        Body: {
            "name": "Fluffy",
            "breed": "Persian",
            "age": 3,
            "color": "White",
            "weight": 4.2,
            "is_neutered": true,
            "description": "A friendly and calm cat"
        }
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Create the cat
                    cat = serializer.save()

                    # Return success response with created cat data
                    response_serializer = CatSerializer(cat)
                    return Response(
                        {
                            "status": "success",
                            "message": f'Cat "{cat.name}" has been successfully added to the database',
                            "cat": response_serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )

            except Exception as e:
                return Response(
                    {"status": "error", "message": f"Failed to create cat: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid data provided",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def adopt(self, request: Request, pk: str = None) -> Response:
        """
        Adopt a cat.

        POST /api/cats/{id}/adopt/
        Body: {"owner_name": "John Doe", "adoption_date": "2025-11-03"}
        """
        cat = self.get_object()

        if cat.is_adopted:
            return Response(
                {"error": f"{cat.name} has already been adopted by {cat.owner_name}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AdoptCatSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    owner_name = serializer.validated_data["owner_name"]
                    adoption_date = serializer.validated_data.get(
                        "adoption_date", timezone.now().date()
                    )

                    cat.adopt(owner_name, adoption_date)

                    return Response(
                        {
                            "message": f"{cat.name} has been successfully adopted by {owner_name}!",
                            "cat": CatSerializer(cat).data,
                        }
                    )
            except Exception as e:
                return Response(
                    {"error": f"Failed to adopt {cat.name}: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def return_to_shelter(self, request: Request, pk: str = None) -> Response:
        """
        Return a cat to the shelter.

        POST /api/cats/{id}/return_to_shelter/
        """
        cat = self.get_object()

        if not cat.is_adopted:
            return Response(
                {"error": f"{cat.name} is not currently adopted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                former_owner = cat.owner_name
                cat.return_to_shelter()

                return Response(
                    {
                        "message": f"{cat.name} has been returned to the shelter",
                        "former_owner": former_owner,
                        "cat": CatSerializer(cat).data,
                    }
                )
        except Exception as e:
            return Response(
                {"error": f"Failed to return {cat.name}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def available(self, request: Request) -> Response:
        """
        Get all available cats for adoption.

        GET /api/cats/available/
        """
        available_cats = Cat.available_cats()
        page = self.paginate_queryset(available_cats)

        if page is not None:
            serializer = CatListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CatListSerializer(available_cats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def adopted(self, request: Request) -> Response:
        """
        Get all adopted cats.

        GET /api/cats/adopted/
        """
        adopted_cats = Cat.adopted_cats()
        page = self.paginate_queryset(adopted_cats)

        if page is not None:
            serializer = CatListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CatListSerializer(adopted_cats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def statistics(self, request: Request) -> Response:
        """
        Get comprehensive statistics about cats.

        GET /api/cats/statistics/
        """
        try:
            # Basic counts
            total_cats = Cat.objects.count()
            adopted_cats = Cat.objects.filter(adoption_date__isnull=False).count()
            available_cats = total_cats - adopted_cats
            adoption_rate = (adopted_cats / total_cats * 100) if total_cats > 0 else 0

            # Age statistics
            age_stats = Cat.objects.filter(age__isnull=False).aggregate(
                average_age=Avg("age"), youngest_age=Min("age"), oldest_age=Max("age")
            )

            # Other statistics
            neutered_cats = Cat.objects.filter(is_neutered=True).count()
            breeds_count = Cat.objects.values("breed").distinct().count()

            # Recent adoptions (last 30 days)
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            recent_adoptions = Cat.objects.filter(
                adoption_date__gte=thirty_days_ago
            ).count()

            stats_data = {
                "total_cats": total_cats,
                "adopted_cats": adopted_cats,
                "available_cats": available_cats,
                "adoption_rate": round(adoption_rate, 2),
                "average_age": (
                    round(age_stats["average_age"], 1)
                    if age_stats["average_age"]
                    else None
                ),
                "youngest_age": age_stats["youngest_age"],
                "oldest_age": age_stats["oldest_age"],
                "neutered_cats": neutered_cats,
                "breeds_count": breeds_count,
                "recent_adoptions": recent_adoptions,
            }

            serializer = CatStatisticsSerializer(stats_data)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Failed to generate statistics: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def breeds(self, request: Request) -> Response:
        """
        Get statistics by breed.

        GET /api/cats/breeds/
        """
        try:
            breed_stats = []
            breeds = (
                Cat.objects.values("breed")
                .annotate(
                    count=Count("id"),
                    adopted_count=Count("id", filter=Q(adoption_date__isnull=False)),
                    average_age=Avg("age"),
                    average_weight=Avg("weight"),
                )
                .exclude(breed__isnull=True)
                .order_by("-count")
            )

            for breed_data in breeds:
                breed = breed_data["breed"]
                count = breed_data["count"]
                adopted = breed_data["adopted_count"]
                adoption_rate = (adopted / count * 100) if count > 0 else 0

                breed_stats.append(
                    {
                        "breed": breed,
                        "count": count,
                        "adoption_rate": round(adoption_rate, 2),
                        "average_age": (
                            round(breed_data["average_age"], 1)
                            if breed_data["average_age"]
                            else None
                        ),
                        "average_weight": (
                            round(float(breed_data["average_weight"]), 2)
                            if breed_data["average_weight"]
                            else None
                        ),
                    }
                )

            serializer = BreedStatisticsSerializer(breed_stats, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Failed to generate breed statistics: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def search(self, request: Request) -> Response:
        """
        Advanced search for cats with multiple criteria.

        GET /api/cats/search/?name=whiskers&breed=persian&available=true
        """
        queryset = self.get_queryset()

        # Apply search filters
        name = request.query_params.get("name", None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        color = request.query_params.get("color", None)
        if color:
            queryset = queryset.filter(color__icontains=color)

        available = request.query_params.get("available", None)
        if available is not None:
            is_available = available.lower() in ["true", "1", "yes"]
            if is_available:
                queryset = queryset.filter(adoption_date__isnull=True)
            else:
                queryset = queryset.filter(adoption_date__isnull=False)

        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CatListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CatListSerializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})
