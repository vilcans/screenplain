
# See http://blog.rutwick.com/use-bottle-python-framework-with-google-app-engine 

from StringIO import StringIO

import bottle
from bottle import route, template, request, response, error, debug
from google.appengine.ext.webapp.util import run_wsgi_app

from screenplain.export.text import to_text

@route('/text', method='POST')
def DisplayForm():
    response.content_type = 'text/plain; charset=utf-8'
    input = StringIO(request.forms.get('data'))
    output = StringIO()
    to_text(input, output)
    return output.getvalue()

def main():
    debug(True)
    run_wsgi_app(bottle.default_app())

@error(403)
def Error403(code):
    return 'Forbidden!'
 
@error(404)
def Error404(code):
    return 'Not found'
 
if __name__=="__main__":
    main()
