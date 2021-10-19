#!/bin/bash

source debian/vars.sh

# the tarball’s root dir is `coreruleset-coreruleset-<SHA>/`
#   - maintaining that SHA would be tedious and prone to forgetting to do it until the first build failed
#   - we can’t use `coreruleset-coreruleset-*` because it is executed as `cd 'coreruleset-coreruleset-*'`
