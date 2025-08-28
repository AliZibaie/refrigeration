from django.db import migrations

def create_refrigerants(apps, schema_editor):
    Refrigerant = apps.get_model('cycle_calculator', 'Refrigerant')

    refrigerants_data = [
        {
            'name': 'R-134a',
            'coolprop_name': 'R134a',
            'description': 'Common automotive and commercial refrigerant with good thermodynamic properties',
            'gwp': 1430,
            'odp': 0.0,
            'safety_class': 'A1',
            'application': 'Automotive air conditioning, commercial refrigeration, medium temperature applications'
        },
        {
            'name': 'R-404A',
            'coolprop_name': 'R404A',
            'description': 'Low temperature commercial refrigerant blend of R-125, R-143a, and R-134a',
            'gwp': 3922,
            'odp': 0.0,
            'safety_class': 'A1',
            'application': 'Commercial freezing, low temperature refrigeration, supermarket refrigeration'
        },
        {
            'name': 'R-410A',
            'coolprop_name': 'R410A',
            'description': 'High efficiency residential and commercial AC refrigerant blend of R-32 and R-125',
            'gwp': 2088,
            'odp': 0.0,
            'safety_class': 'A1',
            'application': 'Residential air conditioning, commercial air conditioning, heat pumps'
        },
        {
            'name': 'R-290',
            'coolprop_name': 'R290',
            'description': 'Natural refrigerant (propane) with excellent thermodynamic properties',
            'gwp': 3,
            'odp': 0.0,
            'safety_class': 'A3',
            'application': 'Domestic refrigeration, small commercial systems, environmentally friendly applications'
        },
        {
            'name': 'R-717',
            'coolprop_name': 'Ammonia',
            'description': 'Natural refrigerant (ammonia) with excellent efficiency for industrial applications',
            'gwp': 0,
            'odp': 0.0,
            'safety_class': 'B2L',
            'application': 'Industrial refrigeration, large cold storage, food processing, ice rinks'
        },
        {
            'name': 'R-22',
            'coolprop_name': 'R22',
            'description': 'Legacy HCFC refrigerant being phased out due to ozone depletion',
            'gwp': 1810,
            'odp': 0.055,
            'safety_class': 'A1',
            'application': 'Legacy air conditioning and refrigeration systems (being phased out)'
        },
        {
            'name': 'R-32',
            'coolprop_name': 'R32',
            'description': 'Low GWP refrigerant used in modern air conditioning systems',
            'gwp': 675,
            'odp': 0.0,
            'safety_class': 'A2L',
            'application': 'Residential and commercial air conditioning, heat pumps'
        },
        {
            'name': 'R-1234yf',
            'coolprop_name': 'R1234yf',
            'description': 'Ultra-low GWP refrigerant for automotive applications',
            'gwp': 4,
            'odp': 0.0,
            'safety_class': 'A2L',
            'application': 'Automotive air conditioning, mobile air conditioning'
        }
    ]

    Refrigerant.objects.all().delete()

    for data in refrigerants_data:
        Refrigerant.objects.create(**data)

def reverse_refrigerants(apps, schema_editor):
    Refrigerant = apps.get_model('cycle_calculator', 'Refrigerant')
    Refrigerant.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('cycle_calculator', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_refrigerants,
            reverse_refrigerants,
        ),
    ]
