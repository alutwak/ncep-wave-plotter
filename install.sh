#!/bin/bash

WAV_ENV_PATH=$PWD/.wave-env

python3 -m pip install virtualenv
virtualenv .wave-env
source .wave-env/bin/activate
pip install .

echo "#!/bin/bash" > ncep-wave-plotter.sh
echo "source $WAV_ENV_PATH/bin/activate" >> ncep-wave-plotter.sh
echo "ncep-wave-plotter \$@" >> ncep-wave-plotter.sh
chmod a+x ncep-wave-plotter.sh



