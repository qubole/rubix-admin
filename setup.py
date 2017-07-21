import os
import versioneer
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

setup(
    name="rubix_admin",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url = "https://github.com/vrajat/rubix_admin.git",
    author="Qubole",
    author_email="dev@qubole.com",
    description="Admin tool for Qubole Rubix",
    packages=find_packages(),
    scripts=[],
    entry_points={
        'console_scripts': ['rubix_admin=rubix_admin.command_line:main'],
    },
    install_requires=required,
    long_description=read('README.md'),
)
