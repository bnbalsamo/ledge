from setuptools import setup, find_packages


# Provided Package Metadata
NAME = "ledge"
DESCRIPTION = "A pluggable webhook catcher."
VERSION = "0.3.0"
AUTHOR = "Brian Balsamo"
AUTHOR_EMAIL = "Brian@BrianBalsamo.com"
URL = 'https://github.com/bnbalsamo/ledge'
PYTHON_REQUIRES= ">=3.6,<4"
INSTALL_REQUIRES = [
    "twisted",
    "environ-config>=19.1.0",
    "structlog",
]
ENTRY_POINTS = {
    'console_scripts': ['ledge=ledge:start'],
}


def readme():
    try:
        with open("README.md", 'r') as f:
            return f.read()
    except:
        return False


# Derived Package Metadata
LONG_DESCRIPTION = readme() or DESCRIPTION
if LONG_DESCRIPTION == DESCRIPTION:
    LONG_DESCRIPTION_CONTENT_TYPE = "text/plain"
else:
    LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"


# Set it up!
setup(
    name=NAME,
    description=DESCRIPTION,
    version=VERSION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    package_dir={"": "src"},
    packages=find_packages(
        where="src"
    ),
    entry_points=ENTRY_POINTS,
    include_package_data=True,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    python_requires=PYTHON_REQUIRES
)
