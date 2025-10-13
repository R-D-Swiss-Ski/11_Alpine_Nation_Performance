#!/bin/bash

LOG_FILE="/startup.log"
pwd >> ${LOG_FILE}

if [ -f ../.streamlit/secrets.toml ]; then
    cp ../.streamlit/secrets.toml ../root/.streamlit/secrets.toml
    echo "secrets.toml copied to root" | tee -a "$LOG_FILE"
    echo "Something went wrong when copying secrets.toml to root" | tee -a "$LOG_FILE"
fi

