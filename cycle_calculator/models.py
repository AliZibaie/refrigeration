from django.db import models


class Refrigerant(models.Model):
    name = models.CharField(max_length=50)
    coolprop_name = models.CharField(max_length=50)
    description = models.TextField()
    gwp = models.IntegerField()
    odp = models.FloatField()
    safety_class = models.CharField(max_length=10)
    application = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Calculation(models.Model):
    CYCLE_CHOICES = [
        ('vapor_compression', 'Vapor Compression'),
        ('absorption', 'Absorption'),
    ]

    EXPANSION_CHOICES = [
        ('throttle', 'Throttle Valve'),
        ('turbine', 'Turbine'),
    ]

    cycle_type = models.CharField(max_length=20, choices=CYCLE_CHOICES)
    refrigerant = models.ForeignKey(Refrigerant, on_delete=models.CASCADE)
    expansion_device = models.CharField(max_length=10, choices=EXPANSION_CHOICES, default='throttle')

    # Common parameters
    evaporator_temp = models.FloatField()
    condenser_temp = models.FloatField()

    # Absorption specific
    generator_temp = models.FloatField(null=True, blank=True)
    absorber_temp = models.FloatField(null=True, blank=True)

    # Results
    cop = models.FloatField(null=True, blank=True)
    cooling_capacity = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_cycle_type_display()} - {self.refrigerant} ({self.created_at})"


class StatePoint(models.Model):
    calculation = models.ForeignKey(Calculation, on_delete=models.CASCADE)
    point_number = models.IntegerField()
    temperature = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    enthalpy = models.FloatField(null=True, blank=True)
    entropy = models.FloatField(null=True, blank=True)
    quality = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ['calculation', 'point_number']
