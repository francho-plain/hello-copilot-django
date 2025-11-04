from rest_framework import serializers
from .models import Cat
from decimal import Decimal
from typing import Dict, Any


class CatSerializer(serializers.ModelSerializer):
    """
    Serializer for Cat model with additional computed fields.
    
    This serializer provides a comprehensive representation of cat data
    for API responses, including computed properties and validation.
    """
    
    # Read-only computed fields
    is_adopted = serializers.ReadOnlyField()
    age_display = serializers.ReadOnlyField()
    weight_display = serializers.ReadOnlyField()
    status_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Cat
        fields = [
            'id',
            'name',
            'breed',
            'age',
            'color',
            'weight',
            'is_neutered',
            'owner_name',
            'adoption_date',
            'description',
            'created_at',
            # Computed fields
            'is_adopted',
            'age_display',
            'weight_display',
            'status_display',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'is_adopted',
            'age_display',
            'weight_display',
            'status_display',
        ]
    
    def validate_name(self, value: str) -> str:
        """Validate cat name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Cat name cannot be empty")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Cat name must be at least 2 characters long")
        
        # Check for duplicate names (only during creation)
        cleaned_name = value.strip().title()
        if not self.instance:  # Creating new cat
            if Cat.objects.filter(name__iexact=cleaned_name).exists():
                raise serializers.ValidationError(
                    f"A cat with the name '{cleaned_name}' already exists. Please choose a different name."
                )
        
        return cleaned_name
    
    def validate_breed(self, value: str) -> str:
        """Validate cat breed."""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Breed name must be at least 2 characters long")
        return value.strip().title() if value else value
    
    def validate_color(self, value: str) -> str:
        """Validate cat color."""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Color description must be at least 2 characters long")
        return value.strip().title() if value else value
    
    def validate_age(self, value: int) -> int:
        """Validate cat age."""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("Age cannot be negative")
            if value > 30:
                raise serializers.ValidationError("Age seems unrealistic for a cat")
        return value
    
    def validate_weight(self, value: Decimal) -> Decimal:
        """Validate cat weight."""
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError("Weight must be positive")
            if value > 20:  # Very large cat would be around 20kg
                raise serializers.ValidationError("Weight seems unrealistic for a cat")
        return value
    
    def validate_description(self, value: str) -> str:
        """Validate cat description."""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long")
        return value.strip() if value else value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-field validation."""
        adoption_date = attrs.get('adoption_date')
        owner_name = attrs.get('owner_name')
        
        # Check adoption consistency
        if adoption_date and not owner_name:
            raise serializers.ValidationError(
                "Adopted cats must have an owner name"
            )
        
        if owner_name and not adoption_date:
            raise serializers.ValidationError(
                "Cats with owners must have an adoption date"
            )
        
        return attrs


class CatListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for cat listings.
    
    Used for list views where we want to minimize data transfer
    while still providing essential information.
    """
    
    is_adopted = serializers.ReadOnlyField()
    status_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Cat
        fields = [
            'id',
            'name',
            'breed',
            'age',
            'color',
            'is_adopted',
            'status_display',
            'created_at',
        ]


class CatStatisticsSerializer(serializers.Serializer):
    """
    Serializer for cat statistics data.
    
    Used to return aggregated statistics about cats in the database.
    """
    
    total_cats = serializers.IntegerField()
    adopted_cats = serializers.IntegerField()
    available_cats = serializers.IntegerField()
    adoption_rate = serializers.FloatField()
    
    # Age statistics
    average_age = serializers.FloatField(allow_null=True)
    youngest_age = serializers.IntegerField(allow_null=True)
    oldest_age = serializers.IntegerField(allow_null=True)
    
    # Other statistics
    neutered_cats = serializers.IntegerField()
    breeds_count = serializers.IntegerField()
    
    # Recent activity
    recent_adoptions = serializers.IntegerField()


class AdoptCatSerializer(serializers.Serializer):
    """
    Serializer for cat adoption actions.
    
    Used when processing adoption requests.
    """
    
    owner_name = serializers.CharField(
        max_length=100,
        help_text="Name of the new owner"
    )
    adoption_date = serializers.DateField(
        required=False,
        help_text="Adoption date (defaults to today if not provided)"
    )
    
    def validate_owner_name(self, value: str) -> str:
        """Validate owner name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Owner name cannot be empty")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Owner name must be at least 2 characters long")
        
        return value.strip().title()


class BreedStatisticsSerializer(serializers.Serializer):
    """
    Serializer for breed statistics.
    
    Returns information about cat breeds in the database.
    """
    
    breed = serializers.CharField()
    count = serializers.IntegerField()
    adoption_rate = serializers.FloatField()
    average_age = serializers.FloatField(allow_null=True)
    average_weight = serializers.FloatField(allow_null=True)