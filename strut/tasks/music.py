import os
import subprocess
from tempfile import mkstemp

from strut.mediaresolvers.youtube import YouTubeResolver
from strut.models import File, Song, SongJob, SongMeta


def process_songjob(job_id):
    # TODO: Needs to upload to GCS
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

    resolver = YouTubeResolver(meta, job)

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

    message = {"type": "load", "data": file.hexdigest()}
    for device in Device.objects.filter(
        deviceassociation__organization__organizationmember__is_active=True,
        deviceassociation__organization__organizationmember__user__playlist__playlistsong__song__file=file,
    ):
        device.send_message(message)

    job.record(status=SongJob.Status.Success)

    # subprocess.check_output(['afplay', output])
