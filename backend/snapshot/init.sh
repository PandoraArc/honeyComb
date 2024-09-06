#!/bin/bash

if [ -f ./data/data.db ]; then
    echo "Database already exists"
else
    echo "Creating database"
    sqlite3 ./data/data.db < ./snapshot/init.sql
fi

uvicorn app.main:app --host 0.0.0.0 --port 80 --reload