#!/bin/bash

if [[ -e /opt/deploy-to-kubernetes/tools/bash_colors.sh ]]; then
    source /opt/deploy-to-kubernetes/tools/bash_colors.sh
else
    inf() {
        echo "$@"
    }
    anmt() {
        echo "$@"
    }
    good() {
        echo "$@"
    }
    err() {
        echo "$@"
    }
    critical() {
        echo "$@"
    }
    warn() {
        echo "$@"
    }
fi

# probably not ideal but needed for working on MacOS
# will also need to manually add:
# /data to Docker -> Preferences -> File Sharing
if [[ ! -e /data ]]; then
    sudo mkdir -p -m 777 /data
fi

os_type=`uname -s`
case "$os_type" in
    Linux*)
        inf "Setting up environment for Linux"
        test_pkman=$(which dpkg | wc -l)
        if [[ "${test_pkman}" == "1" ]]; then
            test_deb=$(dpkg -s python3-distutils | grep 'install ok installed' | wc -l)
            if [[ "${test_deb}" == "0" ]]; then
                warn "using sudo to install python3-distutils python3-tk on ubuntu"
                sudo apt-get install python3-distutils python3-tk
            fi
        fi
        ;;
    Darwin*)
        inf "Setting up environment for MacOS"
        ;;
    *)
        warn "Unsupported OS, exiting."
        exit 0
        ;;
esac

down_dir="0"
debug="0"
compose="dev.yml"
for i in "$@"
do
    # just redis and minio testing:
    if [[ "${i}" == "-d" ]]; then
        debug="1"
    # end-to-end integration testing:
    elif [[ "${i}" == "-a" ]]; then
        debug="1"
        compose="integration.yml"
    # end-to-end integration testing with notebook editing
    # over <repo base>/docker/notebooks:
    elif [[ "${i}" == "-j" ]]; then
        debug="1"
        compose="notebook-integration.yml"
    fi
done

anmt "-------------"
if [[ "${compose}" == "dev.yml" ]]; then
    inf "starting redis and minio"
elif [[ "${compose}" == "integration.yml" ]]; then
    inf "starting end-to-end integration stack: redis, minio, workers and jupyter"
elif [[ "${compose}" == "notebook-integration.yml" ]]; then
    inf "starting end-to-end with notebook integration stack: redis, minio, workers and jupyter"
else
    err "unsupported compose file: ${compose}"
    exit 1
fi

if [[ ! -e ./${compose} ]]; then
    pushd compose >> /dev/null
    down_dir="1"
fi
docker-compose -f ./${compose} up -d

if [[ "${down_dir}" == "1" ]]; then
    popd >> /dev/null
fi

if [[ "${compose}" == "dev.yml" ]]; then
    good "started redis and minio"
elif [[ "${compose}" == "integration.yml" ]]; then
    good "started end-to-end integration stack: redis, minio, workers and jupyter"
fi

exit 0
