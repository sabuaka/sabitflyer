from setuptools import setup, find_packages

setup(
    name='sabitflyer',
    packages=['sabitflyer'],
    version='1.1.0',
    description='Bitflyer API Library for Python',
    author='sabuaka',
    author_email='sabuaka-fx@hotmail.com',
    url="https://github.com/sabuaka/sabitflyer",
    install_requires=['requests', 'urllib3', 'websocket-client']
)
