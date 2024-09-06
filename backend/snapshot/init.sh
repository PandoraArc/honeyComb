#!/bin/bash

if [ -f ./data/data.db ]; then
    echo "Database already exists"
else
    echo "Creating database"
    sqlite3 ./data/data.db < ./init.sql
fi