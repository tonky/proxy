from urlparse import urljoin
import re


# point any relaitive links to be served via tunnel
# i.e. '(stuff)="/<link>"' to '(stuff)="<client_tunnel_url>/link"'
# replace relative links in js and css as well
def _replace_relative(content, client_host, target_base):
    tunneled = "\g<1>\g<2>%s/%s/\g<3>\g<4>" % (client_host, target_base)
    return re.sub("(url\(|\[|data-source=|data-url=|src=|action=|href=)('|\")(\S*)('|\")", tunneled, content, flags=re.I)

# absolute links are easier, as we can just add a tunnel url in front of absolute remote one
def _replace_absolute(content, client_host, target_base):
    return content.replace(target_base, "%s/%s" % (client_host, target_base))

def fix_format(content):
    # remove extraneous whitespace around "="
    trimmed = re.sub("\s*=\s*", "=", content)

    # only add quotes for the links starting with "/", breaks some js otherwise
    return re.sub("(?P<key>action)=(?P<value>/[a-zA-Z]+)", '\g<key>="\g<value>"', trimmed, flags=re.I)

def replace_links(content, client_host, target_base):
    # remove any absolute links, then treat them all as relative
    relative = re.sub(target_base, '', content)
    fixed =  _replace_relative(fix_format(relative), client_host, target_base)
    # fix resulting double slash at the end of target_base
    return re.sub(target_base+"//", target_base+"/", fixed)
