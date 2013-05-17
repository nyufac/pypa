from flask import Flask, request
from json import loads as loadjson, dumps as dumpjson

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:pypa.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
orm = declarative_base()
orm.query = db_session.query_property()
app = Flask(__name__)


class Paste(orm):
    __tablename__ = 'pastes'
    id    = Column(String(48), primary_key=True)
    lang  = Column(String(50), unique=False)
    src   = Column(Text(),     unique=True)

    def __init__(self, source, lang=None):
        self.lang  = lang
        self.src = source

    def __repr__(self):
        return '<User %r>' % (self.name)


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def latest_pastes():
    return 'Latest paste list'

@app.route('/new')
def paste_form():
    return 'Paste form'

@app.route('/submit')
def receive_paste():
    paste = request.form('paste')
    lang  = request.form('lang')
    return 'Paste receiving'

@app.route('/highlight')
def do_highlight():
    source = request.form('source')

    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter

    return highlight(source, PythonLexer(), HtmlFormatter())

@app.route('/view/<pasteid>')
def show_paste(pasteid):
    return 'Showing paste'

if __name__ == '__main__':
    orm.metadata.create_all(bind=engine)
    app.run()
