from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class ColdStorageProject(models.Model):
    STORAGE_TYPES = [
        ('fruit', 'Fruits & Vegetables'),
        ('meat', 'Meat Products'),
        ('dairy', 'Dairy Products'),
        ('frozen', 'Frozen Foods'),
        ('medicine', 'Pharmaceuticals'),
        ('general', 'General Storage'),
    ]

    INSULATION_TYPES = [
        ('polyurethane', 'Polyurethane'),
        ('polystyrene', 'Polystyrene'),
        ('mineral_wool', 'Mineral Wool'),
        ('vacuum_panels', 'Vacuum Panels'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPES)

    # Dimensions
    length = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(200)])
    width = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(200)])
    height = models.FloatField(validators=[MinValueValidator(2), MaxValueValidator(20)])

    # Environmental conditions
    outdoor_temp = models.FloatField(validators=[MinValueValidator(-10), MaxValueValidator(50)])
    outdoor_humidity = models.FloatField(validators=[MinValueValidator(20), MaxValueValidator(100)])
    indoor_temp = models.FloatField(validators=[MinValueValidator(-30), MaxValueValidator(20)])
    indoor_humidity = models.FloatField(validators=[MinValueValidator(40), MaxValueValidator(95)])

    # Insulation
    insulation_type = models.CharField(max_length=20, choices=INSULATION_TYPES)
    insulation_thickness = models.FloatField(validators=[MinValueValidator(0.05), MaxValueValidator(0.5)])

    # Products and loads
    product_mass = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100000)])
    daily_product_input = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10000)])
    number_of_workers = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    working_hours = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(24)])

    # Equipment
    lighting_power = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10000)])
    fan_power = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5000)])
    door_openings = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_storage_type_display()}"

    @property
    def volume(self):
        return self.length * self.width * self.height

    @property
    def floor_area(self):
        return self.length * self.width

    @property
    def total_surface_area(self):
        return 2 * (self.length * self.width + self.length * self.height + self.width * self.height)


class CoolingLoadResult(models.Model):
    project = models.OneToOneField(ColdStorageProject, on_delete=models.CASCADE, related_name='result')

    transmission_load = models.FloatField()
    infiltration_load = models.FloatField()
    product_load = models.FloatField()
    internal_load = models.FloatField()
    respiration_load = models.FloatField()

    total_load = models.FloatField()
    safety_factor = models.FloatField(default=1.15)
    design_load = models.FloatField()

    calculation_details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Results for {self.project.name}"

    @property
    def total_load_kw(self):
        return self.total_load / 1000

    @property
    def design_load_kw(self):
        return self.design_load / 1000

    @property
    def refrigeration_tons(self):
        return self.design_load / 3516.85
