#!/bin/bash

# Pass in name and status
function die { echo $1: status $2 ;  exit $2; }

echo ${TEST_DIR}

ln -s ${LOCAL_TEST_DIR}/rawsim_numEvent20.root || die 'Failure getting input file' $?
(cmsRun ${LOCAL_TEST_DIR}/test_ntuple_cfg.py ) || die 'Failure using test_ntuple_cfg.py' $?
[ -e rawsim_numEvent20.root ] && rm rawsim_numEvent20.root

PYTHONTEST=${CMSSW_BASE}/src/SLHCL1TrackTriggerSimulations/NTupleTools/python/test
(python ${PYTHONTEST}/testNTuple.py ${LOCAL_TOP_DIR}/test_ntuple.root ) || die 'Failure using testNTuple.py' $?
#[ -e test_ntuple.root ] && rm test_ntuple.root

