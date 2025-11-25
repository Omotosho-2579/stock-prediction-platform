# setup.py

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='stock-prediction-platform',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='AI-powered stock prediction platform with advanced ML models and trading signals',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Omotosho-2579/stock-prediction-platform',
    project_urls={
        'Bug Tracker': 'https://github.com/Omotosho-2579/stock-prediction-platform/issues',
        'Documentation': 'https://github.com/Omotosho-2579/stock-prediction-platform/docs',
        'Source Code': 'https://github.com/Omotosho-2579/stock-prediction-platform',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'notebooks', 'scripts']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Natural Language :: English',
    ],
    keywords='stock prediction machine-learning trading finance AI deep-learning',
    python_requires='>=3.9',
    install_requires=[
        'streamlit>=1.32.0',
        'pandas>=2.2.0',
        'numpy>=1.26.0',
        'matplotlib>=3.8.0',
        'seaborn>=0.13.0',
        'plotly>=5.19.0',
        'yfinance>=0.2.37',
        'scikit-learn>=1.4.0',
        'xgboost>=2.0.0',
        'tensorflow>=2.16.0',
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.0',
        'python-dotenv>=1.0.0',
        'SQLAlchemy>=2.0.0',
        'pandas-ta>=0.3.14b0',
    ],
    extras_require={
        'dev': [
            'pytest>=8.1.0',
            'pytest-cov>=4.1.0',
            'black>=24.2.0',
            'flake8>=7.0.0',
            'mypy>=1.9.0',
        ],
        'docs': [
            'sphinx>=7.2.0',
            'sphinx-rtd-theme>=2.0.0',
        ],
        'sentiment': [
            'nltk>=3.8.0',
            'textblob>=0.18.0',
            'vaderSentiment>=3.3.0',
            'newsapi-python>=0.2.7',
        ],
        'notifications': [
            'python-telegram-bot>=20.8',
            'discord-webhook>=1.3.0',
        ],
        'social': [
            'praw>=7.7.0',
            'tweepy>=4.14.0',
        ],
        'all': [
            'pytest>=8.1.0',
            'pytest-cov>=4.1.0',
            'black>=24.2.0',
            'flake8>=7.0.0',
            'mypy>=1.9.0',
            'sphinx>=7.2.0',
            'sphinx-rtd-theme>=2.0.0',
            'nltk>=3.8.0',
            'textblob>=0.18.0',
            'vaderSentiment>=3.3.0',
            'newsapi-python>=0.2.7',
            'python-telegram-bot>=20.8',
            'discord-webhook>=1.3.0',
            'praw>=7.7.0',
            'tweepy>=4.14.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'stock-predict=app.main:main',
            'stock-migrate=scripts.migrate_database:main',
            'stock-digest=scripts.send_daily_digest:main',
        ],
    },
    include_package_data=True,
    package_data={
        'assets': ['*.png', '*.ico', '*.css', 'animations/*.json'],
    },
    zip_safe=False,
    platforms='any',
)