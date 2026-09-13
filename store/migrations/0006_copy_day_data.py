from django.db import migrations


def copy_day(apps, schema_editor):
    LunarEvent = apps.get_model('your_app', 'LunarEvent')
    for e in LunarEvent.objects.all():
        e.day_from = e.day
        e.day_to = e.day
        e.save()


class Migration(migrations.Migration):

    dependencies = [
        ('your_app', '0005_auto_20260913_xxxx'),  # এখানে আগের migration-এর নাম দিন
    ]

    operations = [
        migrations.RunPython(copy_day),
    ]