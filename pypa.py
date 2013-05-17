from flask import Flask, request, redirect, url_for, render_template, abort

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///pypa.db', convert_unicode=True)
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
        self.lang = lang
        self.src  = source
        self.id   = self.__uid()

    def __uid(self):
        gl   = ['i', 'ya', 'yu', 'o', 'a', 'eee', 'iii', 'u']
        sogl = ['m', 'n', 'l', 'r', 'b', 'zh', 'h', 'k']

        from random import shuffle, sample

        uid = sample(gl,5) + sample(sogl,5)
        shuffle(uid)
        return ''.join(uid)

    def __repr__(self):
        return '<Paste #%s (%r)>' % (self.id, self.lang)

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def paste_form():
    from pygments.lexers import get_all_lexers
    languages = list(get_all_lexers())
    languages.sort()
    return render_template('new.html', languages=languages)

@app.route('/submit', methods=["POST"])
def receive_paste():
    paste = Paste(request.form['paste'], request.form['lang'])
    from pygments.lexers import get_all_lexers
    languages = set(map(lambda l:l[1][0], list(get_all_lexers())))
    if paste.lang not in languages or len(paste.src) > 10**5:
        abort(403)
    db_session.add(paste)
    db_session.commit()
    return redirect(url_for('show_paste', pasteid = paste.id))

def do_highlight(paste):
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name 
    from pygments.formatters import HtmlFormatter

    lexer = get_lexer_by_name(paste.lang, stripall=True)

    return highlight(paste.src, lexer, HtmlFormatter()), HtmlFormatter().get_style_defs('.highlight')

@app.route('/<pasteid>')
def show_paste(pasteid):
    paste    = Paste.query.filter(Paste.id == pasteid).first()
    if paste == None:
        abort(404)
    rendered, css = do_highlight(paste)
    return render_template('show.html', paste=paste, rendered=rendered, css=css)

if __name__ == '__main__':
    orm.metadata.create_all(bind=engine)
    app.run()
