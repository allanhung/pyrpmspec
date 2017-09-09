# pyrpmspec

Generate RPM Spec file

# Install

    git clone https://github.com/allanhung/pyrpmspec
    pip install pyrpmspec/
    
# Usage

    export RPMBUILDROOT=/root/rpmbuild
    export SRCDIR=/opt/grafana/sources
    export SPECSDIR=/opt/grafana/specs
    
    pyrpmspec go https://github.com/grafana/grafana 4.5.0-beta1 --tag v
