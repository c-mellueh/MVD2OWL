from setuptools import setup
from setuptools import find_packages
import os
thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = [] # Here we'll get: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()


setup(
    name='mvd2onto',
    version='0.0.1',
    packages=[find_packages()],
    url='https://github.com/krapottke1312/mvd2onto',
    license='',
    author='Christoph Mellüh',
    author_email='christoph@mellueh.de',
    description='This is my Thesis',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'client = mvd2onto.visualization:main',
        ],

    }
)
