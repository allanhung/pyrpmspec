#!/usr/bin/python

from jinja2 import Template
from bs4 import BeautifulSoup as bs
import urllib3
import collections

template_dir = '/usr/share/pyrpmspec'

def render_template(template_str, template_dict, output_file):
    #from jinja2 import Environment, FileSystemLoader
    #env = Environment(loader=FileSystemLoader(searchpath="/root"))
    #template = env.get_template('test.html')
    #output_from_parsed_template = template.render(foo='Hello World!')
    output_str = Template(template_str).render(template_dict) if template_dict else template_str
    # to save the results
    if output_file:
        with open(output_file, "wb") as f:
            f.write(output_str+'\n')
    else:
        return output_str

def read_template(filename):
    result=[]
    with open(filename, 'r') as f:
        result = f.read().splitlines()
    return result

def convertUnicodeToString(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convertUnicodeToString, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convertUnicodeToString, data))
    else:
        return data

def get_gopkg_version_dict(url):

    urllib3.disable_warnings()
    http = urllib3.PoolManager()
    req = http.request('GET', url)

    pkg_info = bs(req.data, 'html.parser')
    content = pkg_info.find('div',attrs={"class":"col-sm-3 col-sm-offset-1 versions"}).findAll('div')
    version_dict = {}

    for row in content:
        version_dict[row.find('a').string]=row.find('span').string

    return convertUnicodeToString(version_dict)

