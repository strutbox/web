import os

from invoke import task

os.environ["INVOKE_RUN_ECHO"] = "1"

DOCKER_DB_NAME = os.environ.get("STRUT_DOCKER_DB_NAME", "strut-postgres")


@task
def dropdb(ctx):
    ctx.run(f"docker exec {DOCKER_DB_NAME} dropdb -U postgres strut")


@task
def createdb(ctx):
    ctx.run(f"docker exec {DOCKER_DB_NAME} createdb -U postgres strut")


@task
def psql(ctx):
    ctx.run(f"docker exec -it {DOCKER_DB_NAME} psql -U postgres strut", pty=True)


@task
def rmmigrations(ctx):
    ctx.run("rm -vf strut/migrations/0*.py")


@task
def migrate(ctx):
    ctx.run("strut migrate --generate")


@task
def format(ctx):
    ctx.run("isort -rc .")
    ctx.run("black .")


@task
def load_fixture(ctx):
    import strut

    strut.setup()

    from strut import models

    user = models.User.objects.create(email="m@robenolt.com", is_superuser=True)
    org = models.Organization.objects.create(name="Matt", slug="matt")
    models.OrganizationMember.objects.create(
        organization=org, user=user, role=models.OrganizationMember.Role.Owner
    )
    models.OrganizationDomain.objects.create(organization=org, domain="robenolt.com")

    device = models.Device.objects.create(
        name="Matt Device", serial="0000000000000000", pubkey=b""
    )
    models.DeviceAssociation.objects.create(device=device, organization=org)
    models.LockitronLock.objects.create(lock_id="lock-abc123", name="Matt Lock")
    models.LockitronUser.objects.create(user_id="user-abc123", email=user.email)

    playlist = models.Playlist.objects.create(owner=user)
    models.PlaylistSubscription.objects.create(user=user, playlist=playlist)
    meta = models.SongMeta.objects.create(
        source=models.SongMeta.Source.YouTube, identifier="BB0DU4DoPP4"
    )
    meta.resolver.sync()

    song = models.Song.objects.create(meta=meta, start=0, length=4)
    song.process(user=user, sync=True)
    models.PlaylistSong.objects.create(playlist=playlist, song=song)


@task(name="import")
def import_(ctx, path):
    assert os.path.exists(path)

    import sys
    import json
    from glob import iglob

    users = []

    for path in iglob(os.path.join(path, "users", "*", "*.json")):
        with open(path) as fp:
            users.append(json.load(fp))

    import strut

    strut.setup()

    from strut import models

    org, _ = models.Organization.objects.get_or_create(
        slug="sentry", defaults={"name": "Sentry"}
    )

    for domain in "sentry.io", "getsentry.com":
        models.OrganizationDomain.objects.get_or_create(organization=org, domain=domain)

    for u in users:
        print(f'+ {u["email"]}')
        user, _ = models.User.objects.get_or_create(
            email=models.User.objects.normalize_email(u["email"])
        )

        models.OrganizationMember.objects.create(organization=org, user=user)

        playlist = models.Playlist.objects.create(owner=user)

        models.PlaylistSubscription.objects.create(user=user, playlist=playlist)

        for s in u.get("songs", []):
            s = s["options"]
            if s["duration"] < 1:
                continue
            sys.stderr.write(f'  * {s["video_id"]} ... ')
            sys.stdout.flush()
            try:
                meta = models.SongMeta.objects.get(
                    source=models.SongMeta.Source.YouTube, identifier=s["video_id"]
                )
            except models.SongMeta.DoesNotExist:
                meta = models.SongMeta(
                    source=models.SongMeta.Source.YouTube, identifier=s["video_id"]
                )
                try:
                    meta.resolver.sync()
                except meta.DataUnsynced as e:
                    sys.stderr.write(f"! ({e})\n")
                    sys.stderr.flush()
                    continue

            song, _ = models.Song.objects.get_or_create(
                meta=meta, start=s["start"], length=s["duration"]
            )

            song.process(force=True)

            models.PlaylistSong.objects.create(playlist=playlist, song=song)

            sys.stderr.write("ok\n")
            sys.stderr.flush()


@task
def rebuild(ctx):
    try:
        dropdb(ctx)
    except Exception as e:
        pass
    createdb(ctx)
    migrate(ctx)
