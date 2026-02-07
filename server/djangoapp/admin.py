from django.contrib import admin
from .models import CarMake, CarModel


# Register your models here.

# CarModelInline class
class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1  # Number of empty forms to display
    # Optional: customize which fields to display in the inline
    # fields = ['name', 'type', 'year', 'dealer_id', 'is_available']
    # exclude = ['created_at', 'updated_at']


# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_make', 'type', 'year', 'dealer_id', 'is_available')
    list_filter = ('type', 'year', 'car_make', 'is_available')
    search_fields = ('name', 'car_make__name')
    # Optional: add autocomplete for car_make field
    autocomplete_fields = ['car_make']
    # Optional: organize fields in the edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('car_make', 'name', 'dealer_id')
        }),
        ('Specifications', {
            'fields': ('type', 'year', 'engine_size', 'transmission', 'fuel_type')
        }),
        ('Additional Information', {
            'fields': ('price', 'color_options', 'is_available')
        }),
    )


# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_of_origin', 'founded_year', 'is_popular')
    list_filter = ('is_popular', 'country_of_origin')
    search_fields = ('name', 'description')
    inlines = [CarModelInline]  # Add CarModelInline to show car models directly in car make admin
    # Optional: organize fields in the edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Company Details', {
            'fields': ('country_of_origin', 'founded_year', 'website')
        }),
        ('Status', {
            'fields': ('is_popular',)
        }),
    )


# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)