from setuptools import setup, find_packages

setup(
    name='netbox-ttyd-2',
    version='0.1',
    description='A NetBox plugin to integrate ttyd for Web SSH terminal',
    author='Trae Assistant',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
)
