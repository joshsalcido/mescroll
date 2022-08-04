from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from app.models import Post

class PostForm(FlaskForm):
    user_id = IntegerField('user_id')
    photo = StringField('photo', validators=[DataRequired()])
    caption = TextAreaField('caption')
    location = StringField('location')
