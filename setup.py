import re
from setuptools import setup

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = ''
with open('mal/__init__.py') as f:
    match = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if match is not None:
        version = match.group(1)
    else:
        raise RuntimeError('no version found')

readme = ''
with open('README.md') as f:
    readme = f.read()

extras_require = {
    'docs': ['sphinx==4.5.0']
}

setup(
    name='mal.py',
    author='Skylake-dev',
    url='https://github.com/Skylake-dev/mal.py',
    version=version,
    packages=['mal'],
    license='MIT',
    description='A MyAnimeListAPI wrapper written in Python.',
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    extras_require=extras_require,
    python_requires='>=3.8.0',
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Typing :: Typed'
    ]
)
