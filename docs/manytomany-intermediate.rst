==================================
ManyToMany with intermediate table
==================================

How to implement a ManyToMany relation with an intermediate table.  For the
purposes of this example we will create a form that creates a contact.  A
contact can work for a company (in this example that already exists) and can
have a job title.  Job title is stored on the relationship, because it is
possible for the contact to work for more than one company.

This is what our `models.py` looks like::

  from django.db import models

  class Contact(models.Model):
      """
      In which we store contacts
      """
    
      firstname = models.CharField("First name",
                                   max_length=100,
                                   help_text="Please provide the first name",
                                   null=True,
                                   blank=True
                                   )
      secondname = models.CharField("Second name",
                                    max_length=100,
                                    help_text="Please provide the second name",
                                    null=True,
                                    blank=True
                                    )
      companies = models.ManyToManyField(Company,
                                         through=Employment,
                                         null=True,
                                         blank=True
                                         )
      
  class Company(models.Model):
      """
      In which we store companies
      """
      
      name = models.CharField("Company name",
                              max_length=100,
                              help_text="The company name",
                              null=False,
                              blank=False
                              )
                            
  class Employment(models.Model):
      """
      Stores the relationship between Contact and Company. Augmented with job
      title
      """
      
      contact = models.ForeignKey(Contact)
      company = models.ForeignKey(Company)
      job_title = models.CharField("Job title",
                                   max_length=255,
                                   blank=True,
                                   null=True
                                   )

The goal here is to create a form that looks like a single form, but uses the
Django ModelForm and Crispy Forms infrastructure to generate that form.  The
start of our `forms.py` looks like::

  from django import forms
  
  from crispy_extensions.forms import ModelFormWithFormsets
  from crispy_extensions.helper import FormsetContainer
  from crispy_extensions.layout import InlineFormSet
  
  from crispy_forms import helper
  from crispy_forms import layout
  
  from .models import Company
  from .models import Contact
  from .models import Employment
  
Firstly we want to create our `FormSetContainer`.  This is an attribute added
to the Crispy Forms `helper` object that understands how to create and save
the formset.  You need to create a subclass of FormsetContainer that understands
how to save your formset.  In the case of our example it looks like this::

  class EmploymentContainer(FormsetContainer):
      """Save the employment form(s)"""
      def save(self, boundformset, instance):
          for form in boundformset:
              if form.is_bound and form.changed_data and not form.errors:
                  # Form has been filled in, has changed since instantiation
                  # and contains no errors
                  obj = form.save(commit=False)
                  obj.contact = instance
                  obj.save()

Here we're accepting the input from the form, and adding the 'parent' object
(in this case the Contact) to the 'child' (in this case the Employment) before
saving the newly created child.

Next we define the primary form::

  class ContactForm(ModelFormWithFormsets):
      
      class Meta:
          model = Contact
          fields = ('firstname', 
                    'secondname', 
                    )
          
      @property
      def helper(self):
          myhelper = helper.FormHelper()
          formsets = [EmploymentContainer("contact_employment", EmploymentFormSet, 'employment'),
                      ]
          myhelper.formsets = formsets
          myhelper.layout = layout.Layout(
              layout.Fieldset(
                  'Basic details',
                  'firstname',
                  'secondname',
                  InlineFormSet('No caption',
                                "contact_employment",
                                ),
                  css_class='primary-fields',
                  ),
              layout.ButtonHolder(
                          layout.Submit('save', 'Save', css_class='btn btn-primary',),
                          layout.Button('cancel', 'Cancel', css_class='btn',),
                          css_class="form-actions",
                          ),
          )
          return myhelper

Rather than subclassing from Django's `ModelForm` we subclass from CFE's 
`ModelFormWithFormsets`, which provides the additional layer of self knowledge
that these forms need (by providing a more complex `is_multipart()` and
`is_valid()`).

In addition, we add a `.formsets` property to the Crispy Form `helper` that
contains a list of the formsets to be used within the primary form.

Finally, we use CFE's own layout objects to layout the formset.  In this case
InlineFormSet.  The first parameter is the label, followed by the `id` of the
relevant FormsetContainer (from the list in the formsets property).
