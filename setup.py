from distutils.core import setup
from setuptools import find_packages

setup(
    name="django-phrase",
    version="2.0.0",
    description="Connect your Django apps to Phrase with the powerful in-context-translation solution.",
    long_description=open("README.md").read(),
    author="Phrase",
    author_email="info@phrase.com",
    url="https://github.com/phrase/django-phrase",
    download_url="https://github.com/phrase/django-phrase",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Internationalization",
        "Topic :: Software Development :: Localization",
    ],
    install_requires=["six"],
)
