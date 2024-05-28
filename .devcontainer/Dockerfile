FROM ghcr.io/pulumi/devcontainer:extra

##################################################################################
# Install AWS CLI v2

USER root
RUN echo \
    && export ARCH=$(uname -m | awk '{ if ($1 == "x86_64") print "x86_64"; else if ($1 == "aarch64" || $1 == "arm64") print "aarch64"; else print "unknown" }') \
    && export NAME="aws" \
    && export TEST="${NAME} --version" \
    && export PKG="awscli-exe-linux-${ARCH}.zip" \
    && export URL="https://awscli.amazonaws.com/${PKG}" \
    && export DIR="/tmp/awscli" \
    && echo "---------------------------------------------------------"\
    && echo "INFO[${NAME}] Installed:" \
    && echo "INFO[${NAME}]   Command:        ${NAME}" \
    && echo "INFO[${NAME}]   Package:        ${PKG}" \
    && echo "INFO[${NAME}]   Architecture:   ${ARCH}" \
    && echo "INFO[${NAME}]   Source:         ${URL}" \
    && echo "---------------------------------------------------------"\
    && mkdir -p ${DIR} \
    && ${curl} ${URL} --output ${DIR}/${PKG} \
    && unzip ${DIR}/${PKG} -d ${DIR} \
    && bash -c "${DIR}/aws/install" \
    && ${dir_clean} \
    && ${TEST} \
    && echo

# Apt Packages
ARG APT_PKGS="\
    chromium-browser \
    "
# Apt Packages
RUN echo \
    && export TEST="gh version" \
    && bash -c "apt-get update" \
    && bash -c "apt-get install -y --no-install-recommends -o Dpkg::Options::='--force-confold' ${APT_PKGS}" \
    && ${TEST} \
    && echo

# Install hugo
EXPOSE 1313
RUN set -ex \
    && export arch=$(uname -m | awk '{ if ($1 == "x86_64") print "amd64"; else if ($1 == "aarch64" || $1 == "arm64") print "arm64"; else print "unknown" }') \
    && export urlHugoRelease="https://api.github.com/repos/gohugoio/hugo/releases/latest" \
    && export urlHugoVersion=$(curl -s ${urlHugoRelease} | awk -F '["v,]' '/tag_name/{print $5}') \
    && export urlHugoBase="https://github.com/gohugoio/hugo/releases/download" \
    && export urlHugoBin="hugo_extended_${urlHugoVersion}_Linux-${arch}.deb" \
    && export urlHugo="${urlHugoBase}/v${urlHugoVersion}/${urlHugoBin}" \
    && curl --output /tmp/${urlHugoBin} -L ${urlHugo} \
    && sudo dpkg -i /tmp/${urlHugoBin} \
    && which hugo \
    && hugo version \
    && rm -rf /tmp/* \
    && true

USER vscode
