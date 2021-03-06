import os
import webapp2
import jinja2
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class CoursePaige(Handler):
    def get(self):
        self.render("course_toc.html")

class Stage(Handler):
    def get(self, stage_num):
        self.render("stage{0}.html".format(stage_num))

class Comment(ndb.Model):
    name = ndb.StringProperty()
    comment_content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class CommentsHandler(CoursePaige):
    def get(self):
        comments_query = Comment.query(ancestor=comment_key).order(-Comment.date)
        comments = comments_query.fetch()

        blank_error = self.request.get('blank_error')

        self.render("comments.html", comments=comments, blank_error=blank_error)

    def post(self):
        comment = Comment(parent=comment_key)
        comment.name = self.request.get('name')
        comment.comment_content = self.request.get('comment_content')
        blank_error = ''

        validation = [
            not comment.name.strip(),
            not comment.comment_content.strip(),
            len(comment.name) > 15,
            len(comment.comment_content) > 500,
            ]

        if any(validation):
            blank_error = "Please, fill out both the name and comment sections."
        else:
            comment.put()

        self.redirect('/comments?blank_error='+blank_error)

comment_key = ndb.Key('Comment', 'course_toc')

app = webapp2.WSGIApplication([('/', CoursePaige),
                               ('/stage(\d+)', Stage),
                               ('/comments', CommentsHandler)
                               ],
                                debug=True)