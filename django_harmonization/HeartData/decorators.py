# decorators.print_http_response
# decorate a script that prints to console so it returns an HttpResponse
# from : https://chase-seibert.github.io/blog/2010/08/06/redirect-console-output-to-a-django-httpresponse.html
#
# use like the following in views.py
#  @print_http_response
#  def my_view(request):


import sys
from django.http import HttpResponse


def print_text_response(f):
    class WritableObject:
        def __init__(self):
            self.content = []
        def write(self, string):
            self.content.append(string)

    def new_f(*args, **kwargs):
        printed = WritableObject()
        sys.stdout = printed
        f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        return HttpResponse(printed.content, content_type='text/plain')

    return new_f

def print_html_response(f):
    class WritableObject:
        def __init__(self):
            self.content = []
        def write(self, string):
            self.content.append(string)

    def new_f(*args, **kwargs):
        printed = WritableObject()
        sys.stdout = printed
        f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        return HttpResponse(printed.content)

    return new_f


def _html_wrap_response(content):
    breaked_content = ['<BR>' if c == '\n' else c for c in content ]
    breaked_content.insert(0,'<pre>')
    breaked_content.append('</pre>')
    return breaked_content 

def print_http_response(f):
    """ Wraps a python function that prints to the console, and
    returns those results as a HttpResponse (HTML)"""

    class WritableObject:
        def __init__(self):
            self.content = []
        def write(self, string):
            self.content.append(string)

    def new_f(*args, **kwargs):
        printed = WritableObject()
        sys.stdout = printed
        f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        return HttpResponse(_html_wrap_response(printed.content))

    return new_f

