from urlparse import urljoin
import re


# point any relaitive links to be served via tunnel
# i.e. '(stuff)="/<link>"' to '(stuff)="<client_tunnel_url>/link"'
def _replace_relative(content, client_base, target):
    tunneled = "\g<1>=\g<2>%s/%s/\g<3>\g<4>" % (client_base, target)
    return re.sub("(data-source|data-url|src|action|href)=('|\")/(\S*)('|\")", tunneled, content)

# absolute links are easier, as we can just add a tunnel url in front of absolute remote one
def _replace_absolute(content, client_base, target):
    return content.replace(target, "%s/%s" % (client_base, target))

def replace_links(content, client_base, target):
    absolute = _replace_absolute(content, client_base, target)
    return _replace_relative(absolute, client_base, target)
