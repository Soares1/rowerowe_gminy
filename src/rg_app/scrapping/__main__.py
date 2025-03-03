import click

from .adm_info import save_data
from .coa_download import download_coa_list


@click.group()
def cli():
    pass


@cli.command(help="Download data about administrative units")
@click.option(
    "--output",
    "-o",
    default=".",
    help="Output directory",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
)
def adm(output: str):
    save_data(output)


@cli.command(help="Download Coat Of Arms images")
@click.argument("df_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--limit", "-l", default=0, help="Limit of downloaded images", type=int)
@click.option(
    "--output_dir",
    "-o",
    default=".",
    help="Output directory",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
)
@click.option(
    "--resulting_df_path",
    "-r",
    default=None,
    help="Path to save modified dataframe",
    type=click.Path(dir_okay=False, writable=True),
)
def coa(df_path: str, output_dir: str, resulting_df_path: str | None = None, limit: int = 0):
    download_coa_list(df_path, output_dir, resulting_df_path, limit=limit)


def main():
    cli()


if __name__ == "__main__":
    main()
