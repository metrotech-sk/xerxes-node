from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["static/*"]

setup(name = "xerxes-node",
    version = "0.7",
    description = "Xerxes monitoring node app",
    author = "themladypan",
    author_email = "stanislav@rubint.sk",
    url = "rubint.sk",
    packages = ['xerxes'],
    package_data = {'xerxes' : files },
    scripts = ["xerxes-worker"],
    long_description = """Really long text here.""" 
) 