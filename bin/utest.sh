# This  runs python unit tests.
    python -m unittest discover
    if [[ $? > 0 ]]; then
        echo "build.sh: error in unittests"
        exit 3;
    fi
