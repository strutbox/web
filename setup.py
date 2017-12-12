from setuptools import setup, find_packages


install_requires = []


for r in 'requirements-base.txt', 'requirements.txt':
    with open(r) as fp:
        for l in fp:
            l = l.strip()
            if not l or l[0] == '#':
                continue
            install_requires.append(l)


setup(
    name='strut-web',
    version='1.0.0.dev0',
    packages=find_packages('.'),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'strut-web=strut.cli:main',
        ],
    },
)
