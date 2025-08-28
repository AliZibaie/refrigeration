from django.db import migrations


def create_refrigerants(apps, schema_editor):
    Refrigerant = apps.get_model('cycle_calculator', 'Refrigerant')

    refrigerants_data = [
        {
            'name': 'R134a',
            'coolprop_name': 'R134a',
        },
        {
            'name': 'R410A',
            'coolprop_name': 'R410A',
        },
        {
            'name': 'R404A',
            'coolprop_name': 'R404A',
        },
        {
            'name': 'R290',
            'coolprop_name': 'R290',
        },
        {
            'name': 'R717',
            'coolprop_name': 'NH3',
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
