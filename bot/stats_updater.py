import os

from storage import Storage

storage = Storage()
os.system("cd ../grc_perl && perl readathletestats.pl " + " ".join([str(x) for x in storage.get_members()]))
# os.system("cd ../grc_perl && perl readactivities.pl " + " ".join([str(x) for x in storage.getMembers()]))
