#!/bin/bash

if [[ -e /opt/venv/bin/activate ]]; then
    source /opt/venv/bin/activate
fi

echo "deploying new build"

echo ""
echo "python version:"
which pythono

echo "updating pip"
pip install --upgrade pip

repos="/opt/sa"
echo "updating: ${repos}"
for d in ${repos}; do
    echo ""
    echo "pulling latest: ${d}"
    cd ${d}
    git pull
    echo "installing latest"
    pip install --upgrade -e .
done

echo ""
echo "checking pip versions:"
pip list --format=columns

echo ""
echo "done"
