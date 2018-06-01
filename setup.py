'''setup.py'''
from setuptools import setup
setup(
    name='sabitflyer',
    packages=['sabitflyer'],
    version='2.2.1',
    description='bitFlyer API Library for Python',
    author='sabuaka',
    author_email='sabuaka-fx@hotmail.com',
    url="https://github.com/sabuaka/sabitflyer",
    install_requires=['requests', 'urllib3', 'websocket-client']
)
