#!/bin/bash

TARGET_DIR="datpl/database"
MODEL_URL="https://github.com/sdadas/polish-nlp-resources/releases/download/v1.0/glove.zip"

DATABASE_FILE="vectors.db"
DICTIONARY_FILE="words.txt"
GLOVE_FILE="glove_100_3_polish.txt"

DATABASE_PATH="$TARGET_DIR/$DATABASE_FILE"

# Variables for testing
TABLE_NAME='vectors'
EXPECTED_ROW_COUNT=143605
schema_check_passed=false
row_count_check_passed=false


cleanup_files() {
    rm "$TARGET_DIR/$GLOVE_FILE"
    rm "$TARGET_DIR/$DICTIONARY_FILE"
    echo "GloVe and words files removed."
}

download_model() {
    curl -L -o "${TARGET_DIR}/glove.zip" $MODEL_URL
    unzip "${TARGET_DIR}/glove.zip" -d "$TARGET_DIR"
    rm "${TARGET_DIR}/glove.zip"
}

setup_database() {
    echo "Creating the database. Please wait..."
    python datpl/database/create_database.py \
        --database-path "$TARGET_DIR/$DATABASE_FILE" \
        --dict-path "$TARGET_DIR/$DICTIONARY_FILE" \
        --model-path "$TARGET_DIR/$GLOVE_FILE"
    }

schema_test() {
    EXPECTED_SCHEMA="CREATE TABLE vectors (word VARCHAR(40) PRIMARY KEY, vector BLOB);"

    # Check if the table exists in the database
    if sqlite3 "$DATABASE_PATH" ".table" | grep -wq "$TABLE_NAME"; then
        # Validate schema
        ACTUAL_SCHEMA=$(sqlite3 "$DATABASE_PATH" ".schema $TABLE_NAME")
        if [ "$ACTUAL_SCHEMA" = "$EXPECTED_SCHEMA" ]; then
            echo "Schema for '$TABLE_NAME' is as expected."
            schema_check_passed=true
        else
            echo "Error: Schema for '$TABLE_NAME' does not match the expected schema."
            echo "Expected schema: '$EXPECTED_SCHEMA"
            echo "Actual schema: '$ACTUAL_SCHEMA'"
        fi
    else
        echo "Error: Table '$TABLE_NAME' does not exist in the database."
    fi
}

row_count_test() {
    ROW_COUNT=$(sqlite3 "$DATABASE_PATH" "SELECT COUNT(*) FROM $TABLE_NAME")

    if [ "$ROW_COUNT" -eq "$EXPECTED_ROW_COUNT" ]; then
        echo "Row count in the database is as expected."
        row_count_check_passed=true
    else
        echo "Error: Row count in the database is not as expected."
        echo "Expected row count: $EXPECTED_ROW_COUNT"
        echo "Actual row count: $ROW_COUNT"
    fi

}
run_tests() {
    schema_test
    row_count_test
}


# Main script
download_model
setup_database
run_tests

# Perform cleanup only if both checks pass
if [ "$schema_check_passed" = true ] && [ "$row_count_check_passed" = true ]; then
    cleanup_files
    echo "Setup completed successfully."
else
    echo "Cleanup is not performed because one or more checks failed."
    exit 1
fi