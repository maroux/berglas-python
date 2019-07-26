#!/bin/bash -e

if [[ -z "${PYTHON_VERSIONS}" ]]; then
    echo "Unspecified PYTHON_VERSIONS, cannot proceed"
    exit 1
fi

pip install pip-tools

out_file=requirements/publish.txt
# always rebuild from scratch
rm -f "$out_file"
pip-compile --no-index --no-header requirements/publish.in -o "$out_file"

PYTHON_VERSIONS_ARRAY=$(echo $PYTHON_VERSIONS | tr "," "\n")
for PYTHON_VERSION in $PYTHON_VERSIONS_ARRAY; do
    pip install pip-tools

    python_major_version=$(echo ${PYTHON_VERSION} | cut -f1 -d'.')
    python_minor_version=$(echo ${PYTHON_VERSION} | cut -f2 -d'.')
    suffix="${python_major_version}.${python_minor_version}"
    out_file=requirements/dev-${suffix}.txt

    # always rebuild from scratch
    rm -f "$out_file"

    pip-compile --no-index --no-header requirements/dev.in -o "$out_file"

    # remove "-e ." line - it's expanded to full path by pip-compile
    # which is most likely a developer's home directory
    tail -n +2 "$out_file" > /tmp/tmp.txt
    mv /tmp/tmp.txt "$out_file"
done
