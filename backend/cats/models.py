from django.db import models
from django.utils import timezone
from typing import Self
from decimal import Decimal


class Cat(models.Model):
    """
    Cat model representing cats in the adoption system.
    
    This model mirrors the PostgreSQL table structure created in the database.
    """
    
    # Primary key (auto-generated)
    id = models.AutoField(primary_key=True)
    
    # Basic cat information
    name = models.CharField(
        max_length=100, 
        help_text="The cat's name"
    )
    
    breed = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="The cat's breed (optional)"
    )
    
    age = models.IntegerField(
        blank=True, 
        null=True,
        help_text="The cat's age in years"
    )
    
    color = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="The cat's color/pattern"
    )
    
    weight = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="The cat's weight in kilograms"
    )
    
    # Medical/care information
    is_neutered = models.BooleanField(
        default=False,
        help_text="Whether the cat has been neutered/spayed"
    )
    
    # Adoption information
    owner_name = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Current owner's name (if adopted)"
    )
    
    adoption_date = models.DateField(
        blank=True, 
        null=True,
        help_text="Date when the cat was adopted"
    )
    
    # Additional information
    description = models.TextField(
        blank=True, 
        help_text="Description of the cat's personality and characteristics"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this record was created"
    )
    
    class Meta:
        app_label = 'cats'
        db_table = 'cats'  # Use existing PostgreSQL table
        ordering = ['id']
        verbose_name = 'Cat'
        verbose_name_plural = 'Cats'
    
    def __str__(self) -> str:
        """String representation of the cat."""
        return f"{self.name} ({self.breed or 'Mixed breed'})"
    
    @property
    def is_adopted(self) -> bool:
        """Check if the cat has been adopted."""
        return self.adoption_date is not None
    
    @property
    def age_display(self) -> str:
        """Human-readable age display."""
        if self.age is None:
            return "Age unknown"
        elif self.age == 1:
            return "1 year old"
        else:
            return f"{self.age} years old"
    
    @property
    def weight_display(self) -> str:
        """Human-readable weight display."""
        if self.weight is None:
            return "Weight unknown"
        return f"{self.weight} kg"
    
    @property
    def status_display(self) -> str:
        """Current adoption status."""
        if self.is_adopted:
            return f"Adopted by {self.owner_name}"
        return "Available for adoption"
    
    @classmethod
    def available_cats(cls) -> models.QuerySet[Self]:
        """Get all cats available for adoption."""
        return cls.objects.filter(adoption_date__isnull=True)
    
    @classmethod
    def adopted_cats(cls) -> models.QuerySet[Self]:
        """Get all adopted cats."""
        return cls.objects.filter(adoption_date__isnull=False)
    
    @classmethod
    def by_breed(cls, breed: str) -> models.QuerySet[Self]:
        """Get cats by breed (case-insensitive)."""
        return cls.objects.filter(breed__icontains=breed)
    
    @classmethod
    def neutered_cats(cls) -> models.QuerySet[Self]:
        """Get all neutered cats."""
        return cls.objects.filter(is_neutered=True)
    
    def adopt(self, owner_name: str, adoption_date: models.DateField = None) -> None:
        """Mark this cat as adopted."""
        self.owner_name = owner_name
        self.adoption_date = adoption_date or timezone.now().date()
        self.save()
    
    def return_to_shelter(self) -> None:
        """Return this cat to the shelter (mark as unadopted)."""
        self.owner_name = None
        self.adoption_date = None
        self.save()
    
    def clean(self) -> None:
        """Validate the model data."""
        super().clean()
        
        # Validate age
        if self.age is not None and self.age < 0:
            raise ValueError("Age cannot be negative")
        
        # Validate weight
        if self.weight is not None and self.weight <= 0:
            raise ValueError("Weight must be positive")
        
        # Ensure adoption consistency
        if self.adoption_date and not self.owner_name:
            raise ValueError("Adopted cats must have an owner name")
        
        if self.owner_name and not self.adoption_date:
            raise ValueError("Cats with owners must have an adoption date")
