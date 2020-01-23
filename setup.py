from setuptools import setup

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='sfftk-migrate',
    version='0.1.0.dev0',
    packages=['sfftk_migrate'],
    url='',
    license='Apache 2.0',
    author='Paul K. Korir, PhD',
    author_email='pkorir@ebi.ac.uk, paul.korir@gmail.com',
    description='Migrate older EMDB-SFF files to newer versions',
    long_description_content_type='text/x-rst',
    long_description=LONG_DESCRIPTION,
    install_requires=['lxml'],
    entry_points={
        'console_scripts': [
            'sff-migrate = sfftk_migrate.main:main',
        ]
    },
    package_data={
        'sfftk_migrate': [
            'stylesheets/*.xsl',
        ],
    }
)
