import setuptools
from __init__ import version


with open('README.md') as f:
    desc = f.read()

setuptools.setup(
    name='tmux_dash',
    version=version,
    scripts=['tmux_dash'],
    author='BenJC',
    author_email='benjamin.carrington@gmail.com',
    description='Tmux configuration intended for a dashboard',
    long_description=desc,
    long_description_content_type='text/markdown',
    url='https://github.com/bodneyc/tmux_dash',
    packages=setuptools.find_packages(),
    install_requires=[
        'libtmux'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)'
    ]
)
