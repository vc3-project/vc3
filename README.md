# vc3-glidein

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/69cfa4b889b242df977fbce919312fa5)](https://www.codacy.com/app/LincolnBryant/vc3-glidein?utm_source=github.com&utm_medium=referral&utm_content=vc3-project/vc3-glidein&utm_campaign=badger)

```
Usage: ./vc3-glidein

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit

  Glidein options:
    Control the HTCondor source and configuration

    -w WORKDIR, --workdir=WORKDIR
                        Path to the working directory for the glidein
    -V CONDOR_VERSION, --condor-version=CONDOR_VERSION
                        HTCondor version
    -r CONDOR_URLBASE, --repo=CONDOR_URLBASE
                        URL containing the HTCondor tarball
    -c COLLECTOR, --collector=COLLECTOR
                        collector string e.g., condor.grid.uchicago.edu:9618
    -x LINGER, --lingertime=LINGER
                        idletime in seconds before self-shutdown
    -a AUTH, --auth=AUTH
                        Authentication type (e.g., password, GSI)
    -p PASSWORD, --password=PASSWORD
                        HTCondor pool password
    -W WRAPPER, --wrapper=WRAPPER
                        Path to user job wrapper file
    -P PERIODIC, --periodic=PERIODIC
                        Path to user periodic classad hook script

  Logging options:
    Control the verbosity of the glidein

    -v, --verbose       Sets logger to INFO level (default)
    -d, --debug         Sets logger to DEBUG level

  Misc options:
    Debugging and other options

    -n, --no-cleanup    Do not clean up glidein files after exit
```
