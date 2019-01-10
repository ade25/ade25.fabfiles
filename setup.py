from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='ade25.fabfiles',
      version=version,
      description="Fabric automation",
      long_description=open("README.txt").read() + "\n" +
      open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='Python Fabric',
      author='Ade 25',
      author_email='devops@ade25.de',
      url='http://ade25.de',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ade25'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Fabric<2.0',
          'cuisine',
          'setuptools',
          'slacker',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
