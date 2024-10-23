import typer

from .commands import download

app = typer.Typer()
app.add_typer(download.app, name="download")


@app.callback()
def callback():
    """
    Download playlist CLI app.
    """


if __name__ == "__main__":
    app()
