
FROM apache/hadoop:3.4.0

USER root

# Utilizar los repositorios historicos de CentOS 7.9.2009
RUN sed -i \
    -e 's|^mirrorlist=|#mirrorlist=|' \
    -e 's|^#baseurl=http://mirror.centos.org/centos/\$releasever/|baseurl=https://vault.centos.org/7.9.2009/|' \
    /etc/yum.repos.d/CentOS-Base.repo \
    && yum clean all \
    && yum --disablerepo=epel install -y java-1.8.0-openjdk-devel \
    && yum clean all \
    && rm -rf /var/cache/yum

# Utilizar el JDK instalado y disponer de jps en el PATH
ENV JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk
ENV PATH=/usr/lib/jvm/java-1.8.0-openjdk/bin:$PATH

USER hadoop