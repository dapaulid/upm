from setuptools import setup
from src.upm import __version__ as version

# for local installation, use: pip install . --user  / pip uninstall upm

setup(
    name='upm',
    version=version,
    url='https://github.com/dapaulid/upm',
    author='Daniel Pauli',
    author_email='dapaulid@gmail.com',
    description=('Minimalistic dependency manager for arbitrary files you get from the web.'),
    license='MIT',
    scripts=['src/upm.py'],
    classifiers=[
    ],
)
