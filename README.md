# QKD-Infra-GetKey
<p float="left">
    <img src="upb.png" alt="University Politehnica of Bucharest" width="50"/>
    <img src="Logo.png" alt="Quantum Team @ UPB" width="100"/>
</p>

![QKD Get Key Tool](Screenshot.PNG "QKD Get Key Tool")

# Description

**QKDGKT - QKD Get Key Tool** is a user interface for QKD key access. It allows a priviledged user to access the internal QKD infrastructure at POLITEHNICA Bucharest.

# Installation

In order to install:
 - The software is designed for Linux, but can also work on Windows via WSL (activate WSL if using Windows)
- Install Python 3 and the packages from `requirements.txt` using `pip install -r requirements.txt`
- Rename `config_sample.toml` to `config.toml` and edit your personal details as needed
- Ensure that the `location` entry matches one of the names listed
  in the `[[locations]]` section (for example `Campus`)
- Only the entry for the local location should define an `ipport` value;
  other locations require just a name and an `endpoint`
- To enable self-reporting, set `self_reporting` to `true` and configure
  `report_endpoint` and optionally `report_token` in `config.toml`
- If your self-reporting endpoint uses a self-signed TLS certificate, set
  `report_trust_self_signed = true` in `config.toml`
- Run `python qkdgkt_gui.py` to run the GUI
- Run `python qkdgkt_cli.py --help` to use the CLI
- Use utility functions from `qkdgkt.py` for development

# Usage

To use the QKD system, you need to fill in the following information:
 - Cert: Your personal signed SSL certificate
 - Key: Your personal key
 - CACert (optional): The certificate associated to the CA
 - Source: The source QKD node
 - Destination: The destination QKD node

The same parameters can be supplied via the CLI. For example:

```
python qkdgkt_cli.py --cert my.crt --key my.key --source Campus --destination Precis
```

Add `--cacert ca.crt` if you need to specify a CA certificate.

When `config.toml` contains entries for `cert`, `key`, `cacert`, `pempassword`, or
`location`, the CLI will use those values as defaults. Command line arguments take
precedence over the configuration file.

When querying for a reponse key, you need to:
 1. Select "Response" instead of "Request"
 2. Reverse the source and the destination
 3. Paste the ID of the key to be received in the ID field

# Copyright and license

This work has been implemented by Alin-Bogdan Popa and Bogdan-Calin Ciobanu, under the supervision of prof. Pantelimon George Popescu, within the Quantum Team in the Computer Science and Engineering department,Faculty of Automatic Control and Computers, National University of Science and Technology POLITEHNICA Bucharest (C) 2024. In any type of usage of this code or released software, this notice shall be preserved without any changes.

If you use this software for research purposes, please follow the instructions in the "Cite this repository" option from the side panel.

This work has been partly supported by RoNaQCI, part of EuroQCI, DIGITAL-2021-QCI-01-DEPLOY-NATIONAL, 101091562.
