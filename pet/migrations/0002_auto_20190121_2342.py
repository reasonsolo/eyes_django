# Generated by Django 2.1.5 on 2019-01-21 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contactrelation',
            old_name='UserProfile_a',
            new_name='user_a',
        ),
        migrations.RenameField(
            model_name='contactrelation',
            old_name='UserProfile_b',
            new_name='user_b',
        ),
        migrations.RenameField(
            model_name='petspecies',
            old_name='type',
            new_name='pet_type',
        ),
        migrations.RenameField(
            model_name='privatecontact',
            old_name='UserProfile_a',
            new_name='user_a',
        ),
        migrations.RenameField(
            model_name='privatecontact',
            old_name='UserProfile_b',
            new_name='user_b',
        ),
        migrations.RemoveField(
            model_name='petlostboost',
            name='booster_nickname',
        ),
    ]
