#cv parsing 2/setup.py

from setuptools import setup, find_packages

setup(
    name="app_parsing",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'openai',
        'python-dotenv',
        'langchain',
        'pandas'
    ]
)