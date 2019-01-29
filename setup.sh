if [[ "$(virtualenv --version)" =~ (16[.]) ]]; then
	virtualenv ./venv/
	source ./venv/bin/activate
	pip3 install -r requirements.txt
else
	echo "Please use virtualenv version 16."
fi

echo "Finished setup."
echo "Use 'python3 Particles.py' to run."
