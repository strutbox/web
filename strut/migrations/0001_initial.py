# Generated by Django 2.1 on 2018-08-06 05:06

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('serial', models.CharField(max_length=16)),
                ('pubkey', models.BinaryField()),
                ('settings', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeviceActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[('API_PING', 0), ('API_BOOTSTRAP', 1)], db_index=True)),
                ('message', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('datetime', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checksum', models.BinaryField()),
                ('size', models.PositiveIntegerField()),
                ('time_created', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='FirmwareVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.PositiveSmallIntegerField(choices=[('Device', 0)])),
                ('version', models.TextField()),
                ('name', models.TextField(null=True)),
                ('notes', models.TextField(null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
        migrations.CreateModel(
            name='LockitronLock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lock_id', models.TextField()),
                ('name', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LockitronUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.TextField()),
                ('email', models.TextField()),
                ('first_name', models.TextField(null=True)),
                ('last_name', models.TextField(null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('slug', models.SlugField()),
                ('settings', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('role', models.PositiveSmallIntegerField(choices=[('Owner', 0), ('Member', 10)], default=10)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.Organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.UUIDField(default=uuid.uuid4)),
                ('shared', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlaylistSong',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.Playlist')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlaylistSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.Playlist')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.PositiveIntegerField()),
                ('length', models.PositiveIntegerField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=False)),
                ('file', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='strut.File')),
            ],
        ),
        migrations.CreateModel(
            name='SongJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[('New', 0), ('InProgress', 1), ('Success', 2), ('Failure', 3)], default=0)),
                ('log', models.TextField(default='')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now_add=True)),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.Song')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SongMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.PositiveSmallIntegerField(choices=[('YouTube', 0)])),
                ('identifier', models.TextField()),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_synced', models.DateTimeField(db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeviceAssociation',
            fields=[
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='strut.Device')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='songmeta',
            unique_together={('source', 'identifier')},
        ),
        migrations.AddField(
            model_name='song',
            name='meta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.SongMeta'),
        ),
        migrations.AddField(
            model_name='playlistsong',
            name='song',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.Song'),
        ),
        migrations.AlterUniqueTogether(
            name='organization',
            unique_together={('slug',)},
        ),
        migrations.AlterUniqueTogether(
            name='lockitronuser',
            unique_together={('user_id',)},
        ),
        migrations.AddField(
            model_name='lockitronlock',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.Organization'),
        ),
        migrations.AddIndex(
            model_name='firmwareversion',
            index=models.Index(fields=['-date_created'], name='strut_firmw_date_cr_e4794a_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='firmwareversion',
            unique_together={('channel', 'version')},
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together={('checksum',)},
        ),
        migrations.AddField(
            model_name='deviceactivity',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.Device'),
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together={('serial',)},
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('email',)},
        ),
        migrations.AlterUniqueTogether(
            name='song',
            unique_together={('meta', 'start', 'length')},
        ),
        migrations.AlterUniqueTogether(
            name='playlistsubscription',
            unique_together={('user', 'playlist')},
        ),
        migrations.AlterUniqueTogether(
            name='playlist',
            unique_together={('identifier',)},
        ),
        migrations.AlterUniqueTogether(
            name='organizationmember',
            unique_together={('organization', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='organizationdomain',
            unique_together={('domain',)},
        ),
        migrations.AlterUniqueTogether(
            name='lockitronlock',
            unique_together={('lock_id',)},
        ),
        migrations.AddField(
            model_name='deviceassociation',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strut.Organization'),
        ),
    ]
