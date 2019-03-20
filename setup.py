import setuptools


with open('README.md') as f:
    long_description = f.read()


setuptools.setup(
    name='soong',
    use_scm_version=True,
    description='PostgreSQL utility library for AWS Lambda',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/eladkehat/soong',
    author='Elad Kehat',
    author_email='eladkehat@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Database',
        'Typing :: Typed'
    ],
    keywords='serverless aws labmda postgresql pgsql',
    packages=setuptools.find_packages(exclude=['tests', 'docs']),
    python_requires='>=3.7',
    install_requires=[
        'boto3 ~= 1.7',
        'psycopg2-binary ~= 2.7'
    ],
    setup_requires=['setuptools_scm']
)
