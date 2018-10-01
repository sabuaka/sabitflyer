'''setup.py'''
from setuptools import setup
setup(
    name='sabitflyer',
    packages=['sabitflyer'],
    version='2.7.2',
    description='bitFlyer API Library for Python',
    author='sabuaka',
    author_email='sabuaka-fx@hotmail.com',
    url="https://github.com/sabuaka/sabitflyer",
    install_requires=[
        'requests==2.19.1',
        'urllib3==1.23',
        'websocket-client==0.48.0'
    ]
)
