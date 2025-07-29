#!/bin/bash

# Get parameters
CERT_PATH=$1
KEY_PATH=$2
CACERT_PATH=$3
IPPORT=$4
DESTINATION=$5
PEM_PASSWORD=$6
KEY_ID=$7
CONSUMER=${CONSUMER}

# Export password for the certificate
export SSL_CERT_FILE=$CERT_PATH
export SSL_CERT_KEY=$KEY_PATH
export SSL_CA_CERT=$CACERT_PATH

# Run curl with the provided parameters
DATA=$(echo '{ "key_IDs":[{ "key_ID": "'$KEY_ID'" }] }')
SAE=${DESTINATION}-${CONSUMER}
curl -Ss --cert $CERT_PATH:$PEM_PASSWORD --key $KEY_PATH --cacert $CACERT_PATH -k https://$IPPORT/$CONSUMER/api/v1/keys/$SAE/dec_keys -X POST -H 'Content-Type:application/json' -d "$DATA"
