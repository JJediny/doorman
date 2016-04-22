# -*- coding: utf-8 -*-

from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired

from wtforms.fields import (IntegerField,
                            SelectField,
                            SelectMultipleField,
                            StringField,
                            TextAreaField)
from wtforms.validators import DataRequired


class UploadPackForm(Form):

    pack = FileField(u'Pack configuration', validators=[FileRequired()])


class QueryForm(Form):

    name = StringField('Name', validators=[DataRequired()])
    sql = TextAreaField("Query", validators=[DataRequired()])
    interval = IntegerField('Interval', default=3600, validators=[DataRequired()])
    platform = SelectField('Platform', default='all', choices=[
        ('all', 'All'),
        ('darwin', 'Darwin'),
        ('linux', 'Linux'),
        ('redhat/centos', 'Red Hat/CentOS'),
    ])
    version = StringField('Version')
    description = TextAreaField('Description')
    value = TextAreaField('Value') 
    packs = SelectMultipleField('Packs', default=None, choices=[
    ])
    tags = TextAreaField("Tags")

    def set_choices(self):
        from doorman.models import Pack
        self.packs.choices = Pack.query.with_entities(Pack.name, Pack.name).all()


class UpdateQueryForm(QueryForm):

    def __init__(self, *args, **kwargs):
        super(UpdateQueryForm, self).__init__(*args, **kwargs)
        self.set_choices()
        query = kwargs.pop('obj', None)
        if query:
            self.packs.process_data([p.name for p in query.packs])
            self.tags.process_data('\n'.join(t.value for t in query.tags))


class CreateQueryForm(QueryForm):

    def validate(self):
        from doorman.models import Query
        initial_validation = super(CreateQueryForm, self).validate()
        if not initial_validation:
            return False

        query = Query.query.filter(Query.name == self.name.data).first()
        if query:
            self.name.errors.append(
                "Query with the name {0} already exists!".format(
                self.name.data)
            )
            return False

        # TODO could do some validation of the sql query
        return True


class CreateTagForm(Form):
    value = TextAreaField('Tag', validators=[DataRequired()])


class FilePathForm(Form):
    category = StringField('category', validators=[DataRequired()])
    target_paths = TextAreaField('files', validators=[DataRequired()])
