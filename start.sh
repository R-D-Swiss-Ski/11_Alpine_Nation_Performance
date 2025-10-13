#!/bin/bash

if [-f /.streamlit/secrets.toml] then
    cp ../.streamlit/secrets.toml ../root/.streamlit/secrets.toml
    echo "secrets.toml copied to root"
else
    echo "Something went wrong when copying secrets.toml to root"
fi

