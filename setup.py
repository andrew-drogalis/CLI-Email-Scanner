from os import path
from setuptools import setup, find_packages

"""
    Setup file
    License: GNU
"""

# Content of the README file
current_path = path.abspath(path.dirname(__file__))
with open(path.join(current_path, "README.md")) as f:
    long_description = f.read()


def read_requirements_file(path):
    requires = list()
    f = open(path, "rb")
    for line in f.read().decode("utf-8").split("\n"):
        line = line.strip()
        if line:
            requires.append(line)
    return requires

REQUIRES = read_requirements_file("requirements.txt")

# Setup
setup(
	name='CLI-Email-Scanner',
	version="1.5",
	author='Andrew Drogalis',
    author_email='108765079+andrew-drogalis@users.noreply.github.com',
    description="Utilizes Gmail API to scan for new emails, download the attachments, read the PDF information, and place the attachment in the file system.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/andrew-drogalis/CLI-Email-Scanner',
    python_requires=">=3.6.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIRES,
    license="GNU"
)

