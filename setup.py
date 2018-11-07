from setuptools import setup, find_packages

install_requires= [
    'libnacl>=1.6'
] 

setup(
    name="cswarmd",
    version="0.1.dev0",
    packages=find_packages(),
    author="Ben Metzger",
    description="cryptographic daemon for a semi-autonomous UAV swarm",
    url="http://github.com/UND-UCAS/crypt-swarm",
    install_requires=install_requires,

    entry_points={
        'console_scripts': [
            'cswarmd=cswarmd.__main__:main',
        ],
    }
)
