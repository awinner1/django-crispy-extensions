"""
=================
Class Based Views
=================

In which we define our own class based view mixins.
"""

__author__ = 'Andy Theyers <@offmessage>'
__docformat__ = 'restructuredtext en'


from django.http import HttpResponseRedirect
from django.views.generic.edit import ModelFormMixin


class ModelFormFormsetMixin(ModelFormMixin):
    """
    We add our crispy formsets to a ModelForm CBV
    """
    
    def get_formsetcontainers(self, form):
        """Just in case we want to use this on non-crispy forms"""
        try:
            helper = form.helper
        except AttributeError:
            return []
        return getattr(form.helper, 'formsets', [])
    
    def get_formset_kwargs(self):
        """If your formsets required custom querysets and stuff you'll need
        to override this"""
        kwargs = {}
        kwargs['instance'] = getattr(self, 'object', None)
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs
    
    def save_formsets(self, form, instance=None):
        for formsetcontainer in self.get_formsetcontainers(form):
            formset = getattr(form, formsetcontainer.name, None)
            if formset is not None:
                formsetcontainer.save(formset, instance)
                
    def get_form(self, form_class):
        basekwargs = self.get_formset_kwargs()
        form = super(ModelFormFormsetMixin, self).get_form(form_class)
        formsetcontainers = self.get_formsetcontainers(form)
        for formsetcontainer in formsetcontainers:
            kwargs = basekwargs.copy()
            kwargs['prefix'] = formsetcontainer.prefix
            subform = formsetcontainer.construct(kwargs)
            setattr(form, formsetcontainer.name, subform)
        return form

    def form_valid(self, form):
        """Generic approach to formset saving"""
        if getattr(self, 'object', None) is not None:
            form.save()
        else:
            self.object = form.save()
        self.save_formsets(form, self.object)
        return HttpResponseRedirect(self.get_success_url())
    
