from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0002_alter_question_options_question_order'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='order',
            new_name='order_index',
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['order_index']},
        ),
    ]
