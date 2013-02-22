"""
==================================================
Crispy Extensions for use with Django's FormWizard
==================================================

"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'


from django.utils.translation import ugettext_lazy as _

from .layout import ProperButton
from crispy_forms import layout


def makesteptext(steps):
    human_current = steps.step1 # Silly humans start at 1
    human_last = steps.count
    message = "Step %s of %s" % (human_current, human_last,)
    return message


class ButtonLayout(layout.ButtonHolder):
    """
    A complex button holder for FormWizards
    """
    def __init__(self, steps, **kwargs):
        fields = self._build_fields(steps)
        return super(ButtonLayout, self).__init__(*fields, **kwargs)
    
    def _build_fields(self, steps):
        fields = []
        if steps.prev:
            if steps.prev == steps.first:
                first_step = ProperButton('wizard_goto_step',
                                          steps.first,
                                          'Previous',
                                          input_type='submit',
                                          css_class='btn'
                                          )
                fields.append(first_step)
            else:
                first_step = ProperButton('wizard_goto_step',
                                          steps.first,
                                          'First',
                                          input_type='submit',
                                          css_class='btn'
                                          )
                previous_step = ProperButton('wizard_goto_step',
                                             steps.prev,
                                             'Previous',
                                             input_type='submit',
                                             css_class='btn'
                                             )
                fields.extend([first_step, previous_step])
        if steps.current == steps.last:
            finish = layout.Submit('submit', 'Finish', css_class='btn btn-primary')
            fields.append(finish)
        else:
            next_step = layout.Submit('submit', 'Next', css_class='btn btn-primary')
            fields.append(next_step)
        return fields

