from setuptools import find_packages, setup

setup(name="microservices",
      version = "0.1",
      description = "Fault Tolerant Microservices",
      author = "Julius Taul Madsen and Stephan Thordal Larsen",
      platforms = ["any"],
      license = "BSD",
      packages = find_packages(),
      install_requires = ["Flask==0.10.1",
                          "requests==2.12.1",
                          "wsgiref==0.1.2" ,
                          "redis==2.10.5"],
      )
