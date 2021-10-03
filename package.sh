pyinstaller ./xctest.py --onedir --clean --distpath ./packaged --workpath ./packaged/build --specpath ./packaged
rm -rf ./__pycache__