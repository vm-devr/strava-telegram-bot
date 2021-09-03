import os

import Storage

storage = Storage.Storage()
os.system("cd ../grc_perl && perl readathletestats.pl " + " ".join([str(x) for x in storage.getMembers()]))
# os.system("cd ../grc_perl && perl readactivities.pl " + " ".join([str(x) for x in storage.getMembers()]))
