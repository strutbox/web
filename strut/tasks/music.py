import os
import subprocess
from tempfile import mkstemp

from strut.models import Device, File, Song, SongJob, SongMeta


def process_songjob(job_id):
    try:
        job = SongJob.objects.get(id=job_id, status=SongJob.Status.New)
    except SongJob.DoesNotExist:
        return

    job.record(status=SongJob.Status.InProgress)

    try:
        song = job.song
        meta = song.meta
    except (Song.DoesNotExist, SongMeta.DoesNotExist) as e:
        print(e)
        job.record(str(e), status=SongJob.Status.Failure)
        return

    resolver = meta.resolver
    resolver.bind_job(job)

    try:
        source = resolver.fetch()
    except Exception as e:
        print(e)
        job.record(str(e), status=SongJob.Status.Failure)
        return

    _, output = mkstemp(suffix=".mp3")
    os.unlink(output)

    cmd = [
        "ffmpeg",
        "-i",
        source,
        "-acodec",
        "mp3",
        "-filter:a",
        "loudnorm",
        "-ss",
        str(song.start),
        "-t",
        str(song.length),
        output,
    ]

    job.record(cmd)

    try:
        subprocess.check_output(cmd)
        file = File.objects.upload_from_filename(output)
        Song.objects.filter(id=song.id).update(file=file, is_active=True)
    except Exception as e:
        import traceback

        traceback.print_exc()
        job.record(str(e), status=SongJob.Status.Failure)
        return
    finally:
        for f in source, output:
            try:
                os.unlink(f)
            except FileNotFoundError:
                pass

    for device in Device.objects.filter(
        deviceassociation__organization__organizationmember__is_active=True,
        deviceassociation__organization__organizationmember__user__playlist__playlistsong__song__file=file,
    ).iterator():
        device.load_file(file)

    job.record(status=SongJob.Status.Success)
