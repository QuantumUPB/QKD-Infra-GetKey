# This work has been implemented by Alin-Bogdan Popa and Bogdan-Calin Ciobanu,
# under the supervision of prof. Pantelimon George Popescu, within the Quantum
# Team in the Computer Science and Engineering department,Faculty of Automatic
# Control and Computers, National University of Science and Technology
# POLITEHNICA Bucharest (C) 2024. In any type of usage of this code or released
# software, this notice shall be preserved without any changes.

"""Command line interface for the QKD Get Key Tool."""

import os

import click

import qkdgkt

LOCATIONS = qkdgkt.qkd_get_locations()
LOCAL_LOCATION = qkdgkt.qkd_get_config().get("location")
SOURCE_NAMES = [LOCAL_LOCATION]
DESTINATION_NAMES = qkdgkt.qkd_get_destinations()


def _get_ipport(name: str) -> str:
    """Return the IP and port for a given location name."""
    ipport = next((loc.get("ipport") for loc in LOCATIONS if loc["name"] == name), None)
    if ipport is None:
        raise click.UsageError(f"No IP configured for location {name}.")
    return ipport


@click.command()
@click.option(
    "--cert",
    "cert_path",
    type=click.Path(path_type=str),
    default=lambda: qkdgkt.qkd_get_config().get("cert"),
    show_default="config cert",
    required=False,
    help="Path to the SSL certificate file; if omitted, an insecure HTTP request is made.",
)
@click.option(
    "--key",
    "key_path",
    type=click.Path(path_type=str),
    default=lambda: qkdgkt.qkd_get_config().get("key"),
    show_default="config key",
    required=False,
    help="Path to the private key file; if omitted, an insecure HTTP request is made.",
)
@click.option(
    "--cacert",
    "cacert_path",
    type=click.Path(exists=True, path_type=str),
    default=lambda: qkdgkt.qkd_get_config().get("cacert"),
    show_default="config cacert",
    required=False,
    help="Path to the CA certificate file (optional).",
)
@click.option(
    "--password",
    default=lambda: qkdgkt.qkd_get_config().get("pempassword", ""),
    hide_input=True,
    show_default="config pempassword",
    help="Password for the certificate/private key pair.",
)
@click.option(
    "--source",
    type=click.Choice(SOURCE_NAMES),
    default=lambda: LOCAL_LOCATION,
    show_default="config location",
    help="Local KME name.",
)
@click.option(
    "--destination",
    type=click.Choice(DESTINATION_NAMES),
    required=True,
    help="Remote KME name.",
)
@click.option(
    "--mode",
    type=click.Choice(["Request", "Response"]),
    default="Request",
    show_default=True,
    help="Operation mode.",
)
@click.option(
    "--id",
    "key_id",
    default="",
    help="Key ID (required for response mode).",
)
def main(cert_path, key_path, cacert_path, password, source, destination, mode, key_id):
    """Retrieve keys from the QKD infrastructure via CLI."""
    if source == destination:
        raise click.UsageError("Source and destination must differ.")

    if cert_path and not os.path.isfile(cert_path):
        raise click.BadParameter("cert file not found", param_hint="--cert")
    if key_path and not os.path.isfile(key_path):
        raise click.BadParameter("key file not found", param_hint="--key")

    if not cert_path or not key_path:
        cert_path = ""
        key_path = ""

    if mode == "Response" and not key_id:
        raise click.UsageError("--id is required when --mode Response is selected.")
    if mode == "Request" and key_id:
        raise click.UsageError("--id is only applicable for --mode Response.")

    source_ip = _get_ipport(source)
    kme = source_ip

    result = qkdgkt.qkd_get_key_custom_params(
        destination,
        kme,
        cert_path,
        key_path,
        cacert_path,
        password,
        mode,
        key_id,
    )
    click.echo(result)


if __name__ == "__main__":
    main()
