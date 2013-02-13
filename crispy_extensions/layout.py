"""
=======
Layouts
=======

Additional layout objects.
"""

__author__ = 'Andy Theyers <@offmessage>'
__docformat__ = 'restructuredtext en'


from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms.formsets import DELETION_FIELD_NAME
from django.template import Context
from django.template.loader import render_to_string

from crispy_forms.utils import render_field


TEMPLATE_PACK = getattr(settings, 'CRISPY_TEMPLATE_PACK', 'bootstrap')

class InlineFormSet(object):
    """
    Allows for the rendering of a formset in the middle of a parent form
    
    https://github.com/pydanny/django-uni-form/pull/69/files
    
    Usage::
    
      from crispy_forms.helper import FormHelper
      from crispy_forms.layout import Div, Fieldset, Layout
      
      from crispy_extensions.forms import ModelFormWithFormsets
      
      from models import Contact, Phone
      
      class MyForm(ModelFormWithFormsets):
      
          class Meta:
              model = Contact
            
          @property
          def helper(self):
              myhelper = FormHelper()
          
              myhelper.layout = Layout(
                  Fieldset(
                      'Basic details',
                      'firstname',
                      'secondname',
                      ),
                  InlineFormSet('Phone numbers', 'phonenumbers'),
                  )
              return myhelper
            
            
      class PhoneNumberForm(ModelFormWithFormsets):
      
          class Meta:
              model = Phone
              
          @property
          def helper(self):
              myhelper = FormHelper()
              myhelper.form_tag = False
            
              myhelper.layout = Layout(
                  layout.Div(
                      'phonenumber',
                      ),
                  )
              return myhelper
            
      form = MyForm()
      form.phonenumbers = formset_factory(PhoneNumberForm)
    """
    def __init__(self, title, formset_name, *fields, **kwargs):
        self.title = title
        self.formset_name = formset_name
        self.fields = fields
        self.css = kwargs.get('css_class', u'formset')
        self.group_css = kwargs.get('group_css_class', u'formsetGroup')
        # We're using our own template here - this is an extension to crispy,
        # not part of it (hence not looking up the crispy template pack)
        form_style = kwargs.get('form_style', 'standard')
        if form_style not in ['standard', 'tabular']:
            raise TypeError('form_style can only be standard or tabular')
        if form_style == 'standard':
            self.template = 'crispy_extensions/formset.html'
        elif form_style == 'tabular':
            self.template = 'crispy_extensions/tabular-formset.html'
        self.template = kwargs.get('template', self.template)
        
        
    def render(self, form, *args, **kwargs):
        formset = getattr(form, self.formset_name)
        output = ''
        output += render_to_string(self.template, {'form_title': self.title, 'css': self.css, 'formset': formset, 'group_css': self.group_css})
        for field in self.fields:
            output += render_field(field, form)
        return u''.join(output) # What is this for? Does this ensure unicode?
    
    
class InlineForm(object):
    """
    Allows for the rendering of a single form within another form
    
    https://github.com/pydanny/django-uni-form/pull/69/files
    
    Use as above, but without the formset_factory bit
    """
    def __init__(self, form_name, *fields, **kwargs):
        self.form_name = form_name
        self.fields = fields
        self.css = kwargs.get('css_class', u'')
        self.template = kwargs.get('template', '%s/uni_form.html' % (TEMPLATE_PACK,))
        
    def render(self, form, *args, **kwargs):
        output = '<div class="%s">' % (self.css,)
        inner_form = getattr(form, self.form_name)
        if hasattr(inner_form, 'helper'):
            output += inner_form.helper.layout.render(inner_form)
        else:
            output = render_to_string(self.template, {'form': inner_form})
            for field in self.fields:
                output += render_field(field, form)
        output += u'</div>'
        return u''.join(output) # What is this for? Does this ensure unicode?
    

class GenericContainer(object):
    """
    Layout object. Must have a template specified. If there isn't one, it dies.
    
    I've done this because all the crispy classes are named after specific
    HTML elements, and as soon as you want to change the template the names
    make no sense.
    
    :Parameters:
      template
        (required) template name
      template_map
        (optional) dictionary of the form {'fieldname': 'template_name'}
        which allows for you to override the template used for the given
        field
      all_fields_template
        (optional) template name for rendering *every* field. Overridden by
        `template_map` if an entry exists
        
    any other kwargs are passed through to the template in a dict called extra
    """
    template = None
    template_map = {}
    all_fields_template = None

    def __init__(self, *fields, **kwargs):
        self.fields = fields
        self.template = kwargs.pop('template', self.template)
        if self.template is None:
            raise TypeError("GenericContainer layout requires a template")
        self.template_map = kwargs.pop('template_map', self.template_map)
        self.all_fields_template = kwargs.pop('all_fields_template', self.all_fields_template)
        self.extra = kwargs

    def render(self, form, form_style, context):
        fields = ''
        for field in self.fields:
            template = self.template_map.get(field, self.all_fields_template)
            fields += render_field(field, form, form_style, context, template=template)
        return render_to_string(self.template, Context({'fields': fields, 'extra': self.extra}))


class InlineTabularForm(GenericContainer):
    """
    For rendering our inline forms
    """
    template = 'crispy_extensions/tabular-inline-form.html'
    all_fields_template = 'crispy_extensions/tabular-field.html'
    can_delete = True
    
    def __init__(self, *fields, **kwargs):
        self.can_delete = kwargs.pop('can_delete', self.can_delete)
        if self.can_delete:
            fields = list(fields)
            fields.append(DELETION_FIELD_NAME)
            fields = tuple(fields)
            template_map = kwargs.pop('template_map', self.template_map)
            if DELETION_FIELD_NAME not in template_map:
                template_map[DELETION_FIELD_NAME] = 'crispy_extensions/formset-delete-button.html'
            kwargs['template_map'] = template_map
        return super(InlineTabularForm, self).__init__(*fields, **kwargs)
