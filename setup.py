#!/usr/bin/env python3
"""
ApiForge Setup Script
"""

from setuptools import setup, find_packages
import os

# Read long description from README
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "ApiForge - Lightweight LLM API Gateway & Load Balancer"

setup(
    name='apiforge',
    version='1.0.0',
    description='Lightweight LLM API Gateway & Load Balancer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='AI Project Generator',
    author_email='contact@apiforge.dev',
    url='https://github.com/YOUR_USERNAME/ApiForge',
    license='MIT',
    
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    python_requires='>=3.8',
    
    install_requires=[
        'PyYAML>=6.0',
        'aiohttp>=3.9.0',
    ],
    
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.1.0',
        ],
        'server': [
            'fastapi>=0.104.0',
            'uvicorn[standard]>=0.24.0',
        ],
        'cache': [
            'redis>=5.0.0',
        ],
        'metrics': [
            'prometheus-client>=0.19.0',
        ],
        'dashboard': [
            'streamlit>=1.28.0',
        ],
        'all': [
            'fastapi>=0.104.0',
            'uvicorn[standard]>=0.24.0',
            'redis>=5.0.0',
            'prometheus-client>=0.19.0',
            'streamlit>=1.28.0',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'apiforge=api_forge:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Natural Language :: Chinese (Simplified)',
    ],
    
    keywords='llm api gateway load-balancer openai anthropic proxy',
    
    project_urls={
        'Bug Reports': 'https://github.com/YOUR_USERNAME/ApiForge/issues',
        'Source': 'https://github.com/YOUR_USERNAME/ApiForge',
        'Documentation': 'https://github.com/YOUR_USERNAME/ApiForge#readme',
    },
)
