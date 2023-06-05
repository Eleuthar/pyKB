"""
Define class methods acting like attributes
"""

class Uzr:

    def __init__(self, fname, lname):
        self.fname = fname
        self.lname = lname        
    
    # acts like a getter
    @property
    def fullname(self):
        return '{} {}'.format(self.fname, self.lname)
    
    # allows setting instance attrib via decorated method
    @fullname.setter
    def fullname(self, name):
        fname, lname = name.split(' ')
        self.fname = fname
        self.lname = lname
        
    @fullname.deleter
    def fullname(self)
        self.fname = None
        self.lname = None
        
        
# will print        
uzr_1 = Uzr('Bob', 'Joker')
print(uzr_1.fname, uzr_1.lname)
print(uzr_1.fullname)

# this will rename the above
uzr_1.fullname = 'Joe Rogan'

# set attributes to None
del uzr_1.fullname
