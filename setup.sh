# Create virtual environment
python3 -m venv ./venv

# Install pyinstaller
./venv/bin/pip3 install -r ./requirements.txt

# Package xctest.py
./venv/bin/pyinstaller ./xctest.py --onedir --clean --distpath ./packaged --workpath ./packaged/build --specpath ./packaged

# Remove pycache
rm -rf ./__pycache__