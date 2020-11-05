from setuptools import setup

setup(name='outbreakrprenderer',
      version='0.1.0',
      description='Minecraft resourcepack normalmaps & heightmaps renderer',
      url='https://github.com/Outbreak-Team/outbreak-rp-renderer',
      author='FeelinVoids_',
      author_email='felucca24@gmail.com',
      license='MIT',
      packages=['orp'],
      include_package_data=True,
      entry_points = {
            'console_scripts': ['orp=orp.main:main'],
      },
      install_requires=[],
      zip_safe=False)