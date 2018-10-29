import setuptools

setuptools.setup(
    name='pyparallelize',
    version='0.1',
    packages=setuptools.find_packages(),
    license='AS-IS',
    long_description=open('README.md').read(), requires=['numpy']
)
