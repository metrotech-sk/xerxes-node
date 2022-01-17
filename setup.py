from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["static/*"]

setup(name = "xerxes-node",
    version = "0.1",
    description = "yadda yadda",
    author = "themladypan",
    author_email = "stanislav@rubint.sk",
    url = "rubint.sk",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['src'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'src' : files },
    #'runner' is in the root.
    scripts = ["xerxes-node"],
    long_description = """Really long text here.""" 
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []     
) 