"""Command-line interface for bpmn-onto."""

import click

from bpmn_onto import __version__


@click.group()
@click.version_option(__version__)
def main() -> None:
    """Convert BPMN 2.0 diagrams into validated ISA-95 ontologies."""


@main.command()
@click.argument("bpmn_file", type=click.Path(exists=True))
@click.option(
    "--target",
    type=click.Choice(["isa95"]),
    default="isa95",
    help="Target ontology (only ISA-95 in v1).",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    required=True,
    help="Output Turtle (.ttl) file path.",
)
def convert(bpmn_file: str, target: str, output: str) -> None:
    """Convert a BPMN file into a target ontology."""
    click.echo(f"[stub] would convert {bpmn_file} → {output} ({target})")


if __name__ == "__main__":
    main()
