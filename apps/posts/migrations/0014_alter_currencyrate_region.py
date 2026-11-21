from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_add_approved_source_topic_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencyrate',
            name='region',
            field=models.CharField(
                choices=[
                    ('aden', 'عدن'),
                    ('sanaa', 'صنعاء'),
                    ('hadhramaut', 'حضرموت'),
                    ('marib', 'مأرب'),
                    ('hodeidah', 'الحديدة'),
                    ('ibb', 'إب'),
                ],
                max_length=20,
                verbose_name='المنطقة',
            ),
        ),
    ]
