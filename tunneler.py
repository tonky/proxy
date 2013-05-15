from urlparse import urljoin
import re


# point any relaitive links to be served via tunnel
# i.e. '(stuff)="/<link>"' to '(stuff)="<client_tunnel_url>/link"'
# replace relative links in css as well
def _replace_relative(content, client_host, target_base):
    tunneled = "\g<1>\g<2>%s/%s/\g<3>\g<4>" % (client_host, target_base)
    return re.sub("(data-source=|data-url=|src=|action=|href=|url\()('|\")/(\S*)('|\")", tunneled, content, flags=re.I)

# absolute links are easier, as we can just add a tunnel url in front of absolute remote one
def _replace_absolute(content, client_host, target_base):
    return content.replace(target_base, "%s/%s" % (client_host, target_base))

def fix_format(content):
    # remove extraneous whitespace around "="
    trimmed = re.sub("\s*=\s*", "=", content)

    # add quotes
    return re.sub("(?P<key>action|method)=(?P<value>[a-zA-Z/]+)", '\g<key>="\g<value>"', trimmed, flags=re.I)

def replace_links(content, client_host, target_base):
    absolute = _replace_absolute(fix_format(content), client_host, target_base)
    return _replace_relative(absolute, client_host, target_base)
