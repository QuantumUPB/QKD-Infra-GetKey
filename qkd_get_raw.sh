#!/bin/bash

# Get parameters
CERT_PATH=$1
KEY_PATH=$2
CACERT_PATH=$3
IPPORT=$4
DESTINATION=$5
PEM_PASSWORD=$6
CONSUMER=$(python - <<'PY'
import qkdgkt
print(qkdgkt.qkd_get_myself())
PY
)

ENDPOINT=$(python "$DESTINATION" <<'PY'
import qkdgkt, sys
dest = sys.argv[1]
print(qkdgkt.qkd_get_endpoint(dest))
PY
)

# Export password for the certificate
export SSL_CERT_FILE=$CERT_PATH
export SSL_CERT_KEY=$KEY_PATH

if [ -n "$CACERT_PATH" ]; then
  export SSL_CA_CERT=$CACERT_PATH
  VERIFY_OPT="--cacert $CACERT_PATH"
else
  VERIFY_OPT="-k"
fi

# Run curl with the provided parameters
SAE=$ENDPOINT
curl -Ss --cert $CERT_PATH:$PEM_PASSWORD --key $KEY_PATH $VERIFY_OPT https://$IPPORT/$CONSUMER/api/v1/keys/$SAE/enc_keys
