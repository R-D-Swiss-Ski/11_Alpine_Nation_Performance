#!/bin/bash

LOG_FILE="/app/startup.log"
pwd >> ${LOG_FILE}

if [ -f /.streamlit/secrets.toml ]; then
    cp /.streamlit/secrets.toml /root/.streamlit/secrets.toml
    echo "secrets.toml copied to root" | tee -a "$LOG_FILE"
else
    echo "Something went wrong when copying secrets.toml to root" | tee -a "$LOG_FILE"
fi


# Start Streamlit app
exec streamlit run app.py --server.address=0.0.0.0 --server.port=8501

