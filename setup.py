from setuptools import setup, find_packages

setup(
    name='kaggle_data',
    version='0.4',

    description='An unofficial Kaggle datasets downloader',
    long_description="https://github.com/EKami/kaggle_data/blob/master/README.md",
    url='https://github.com/EKami/kaggle_data',
    author='GODARD Tuatini',
    author_email='tuatinigodard@gmail.com',
    license='MIT',

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],

    keywords='development',
    packages=find_packages(exclude=['tests']),
    install_requires=['mechanicalsoup',
                      'progressbar2'],
)
