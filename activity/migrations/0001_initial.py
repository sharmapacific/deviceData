import unixtimestampfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=500, null=True)),
                ('heart_rate', models.FloatField(blank=True, default=None, null=True)),
                ('respiration_rate', models.FloatField(blank=True, default=None, null=True)),
                ('activity', models.IntegerField(blank=True, null=True)),
                ('timestamp', unixtimestampfield.fields.UnixTimeStampField(auto_now_add=True)),
            ],
        ),
    ]
