import typer

typer_app = typer.Typer()


def callback():
    """
    Bali App entry 4.0 style
    """


def entry(application):
    """Bali application CLI entry
    """

    # When migrate enabled, cli group will changed
    # in <4.0, ENABLE_MIGRATE default is `False`
    # in >=4.0, ENABLE_MIGRATE default is `True`
    #
    # migrate disabled: cli used as same as bali < 4.0
    #   eg: python main.py --http
    # migrate enabled: cli used as same as bali >= 4.0
    #   eg: bali run http
    try:
        from config import settings
        enable_migrate = settings.ENABLE_MIGRATE
    except:
        enable_migrate = False

    if enable_migrate:
        typer_app.command(name='run')(application.launch)
        typer_app.callback()(callback)

        from fastapi_migrate.cli import db
        typer_click_object = typer.main.get_command(typer_app)
        typer_click_object.add_command(db, "db")

        typer_click_object()
    else:
        typer_app.command()(application.launch)
        typer_app()
