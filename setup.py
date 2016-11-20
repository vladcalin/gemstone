from setuptools import setup, find_packages

setup(
    name="pymicroservice",
    version="0.0.1",
    description="Build microservices with Python",
    packages=find_packages(),
    extras_require={
        "flask": ["flask"]
    }
)
