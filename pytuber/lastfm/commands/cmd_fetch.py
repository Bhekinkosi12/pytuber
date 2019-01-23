from typing import List

import click
from tabulate import tabulate

from pytuber.lastfm.services import LastService
from pytuber.models import PlaylistManager, Provider, TrackManager


@click.command("lastfm")
@click.option("--tracks", is_flag=True, help="Update the playlist tracks")
@click.option("--tags", is_flag=True, help="Show the most popular tags")
@click.pass_context
def fetch(ctx: click.Context, tracks: bool = False, tags: bool = False):
    """Fetch tracks and tags information from last.fm."""

    if tracks == tags:
        click.secho(ctx.get_help())
        click.Abort()

    if tracks:
        fetch_tracks()
    elif tags:
        fetch_tags()


def fetch_tracks(*args):
    kwargs = dict(provider=Provider.lastfm)
    if args:
        kwargs["id"] = lambda x: x in args

    playlists = PlaylistManager.find(**kwargs)
    with click.progressbar(playlists, label="Syncing playlists") as bar:
        for playlist in bar:
            tracklist = LastService.get_tracks(
                type=playlist.type, **playlist.arguments
            )

            track_ids: List[str] = []
            for entry in tracklist:
                id = TrackManager.set(
                    dict(artist=entry.artist.name, name=entry.name)
                ).id

                if id not in track_ids:
                    track_ids.append(id)

            PlaylistManager.update(playlist, dict(tracks=track_ids))


def fetch_tags():
    values = [
        (tag.name, tag.count, tag.reach) for tag in LastService.get_tags()
    ]

    click.echo_via_pager(
        tabulate(
            values,
            showindex="always",
            headers=("No", "Name", "Count", "Reach"),
        )
    )
