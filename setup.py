from distutils.core import setup

setup(
    name='django-phrase',
    version='0.0.1',
    description='Connect your Django apps to PhraseApp, the powerful in-context-translation solution.',
    long_description=open('README.rst').read(),
    author='Manuel Boy',
    author_email='info@phraseapp.com',
    url='https://github.com/phrase/django-phrase',
    download_url='https://github.com/phrase/django-phrase',
    license='BSD',
    packages=('django-phrase'),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
    ],
)
