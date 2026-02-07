from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

# Car Make model
class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Enter the car make name (e.g., Toyota, Ford)")
    description = models.TextField(help_text="Enter a description of the car make")
    country_of_origin = models.CharField(max_length=100, blank=True, null=True, help_text="Country where the car make originates from")
    founded_year = models.IntegerField(blank=True, null=True, help_text="Year the company was founded")
    website = models.URLField(max_length=200, blank=True, null=True, help_text="Official website of the car make")
    
    # Any other fields you would like to include
    is_popular = models.BooleanField(default=False, help_text="Is this car make currently popular?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Car Make"
        verbose_name_plural = "Car Makes"


# Car Model model
class CarModel(models.Model):
    # Type choices for the car model
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    COUPE = 'Coupe'
    CONVERTIBLE = 'Convertible'
    HATCHBACK = 'Hatchback'
    TRUCK = 'Truck'
    VAN = 'Van'
    
    TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (COUPE, 'Coupe'),
        (CONVERTIBLE, 'Convertible'),
        (HATCHBACK, 'Hatchback'),
        (TRUCK, 'Truck'),
        (VAN, 'Van'),
    ]
    
    # Many-To-One relationship to Car Make model
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='car_models')
    
    # Dealer ID refers to a dealer created in Cloudant database
    dealer_id = models.IntegerField(help_text="ID of the dealer in Cloudant database")
    
    name = models.CharField(max_length=100, help_text="Enter the car model name (e.g., Camry, Mustang)")
    
    # Type with choices argument
    type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default=SEDAN,
        help_text="Select the car type"
    )
    
    # Year with validators
    year = models.IntegerField(
        validators=[
            MinValueValidator(2015, message="Year must be 2015 or later"),
            MaxValueValidator(2023, message="Year must be 2023 or earlier")
        ],
        help_text="Enter the model year (between 2015-2023)"
    )
    
    # Any other fields you would like to include
    engine_size = models.CharField(max_length=50, blank=True, null=True, help_text="Engine size (e.g., 2.0L, V6)")
    transmission = models.CharField(max_length=50, blank=True, null=True, help_text="Transmission type (e.g., Automatic, Manual)")
    fuel_type = models.CharField(max_length=50, blank=True, null=True, help_text="Fuel type (e.g., Gasoline, Diesel, Electric)")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Approximate price")
    color_options = models.TextField(blank=True, null=True, help_text="Available color options")
    is_available = models.BooleanField(default=True, help_text="Is this model currently available?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"
    
    class Meta:
        ordering = ['car_make', 'name', '-year']
        verbose_name = "Car Model"
        verbose_name_plural = "Car Models"