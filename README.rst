=======================
Crispy forms extensions
=======================

Formsets in Django, it turns out, are hard.  When I came to try and use them
in anger outside the Django admin I found myself tripping over all sorts of
problems.  And as soon as I tried to use them in combination with the excellent
`Crispy Forms`_ I found yet more problems.

Googling and StackOverflow both showed that lots (and I mean *lots*) of people
were having very similar problems, but no one appears to have tackled it in a
generic and repeatable way.  In addition, rightly or wrongly, some projects
have referred to the use of formsets as "an edgecase" and have deliberately
exclude considering them.  This simplifies the project, but often means that
not only are they not considered, they're nigh on impossible to implement within
that framework.

This project attempts to resolve some of those problems.

It is designed with the following philosophy in mind.  If you disagree with any
of the following statements then this may not be the project for you:

 * Forms should *completely* understand themselves (how to lay themselves out,
   how to save their contents, *everything*)
 * The ``helper`` and ``layout`` approach taken by `Crispy Forms`_ is a good
   one, or at the very least one worth extending to get the benefits that 
   `Crispy Forms` bring
 * Django's Class Based Views are a **Good Thing**
 
To date all I'm doing is scratching my own itch, which is as follows:

 * I am using the twitter bootstrap template pack, so no other template packs
   are supported yet (shouldn't be hard to fix though)
 * I want inline formsets at any point within a form, rendered as a table
 * I am only working with ModelForms at the moment (the source for this comes
   from a CRUD heavy application)
   
What it **does** solve:

 * Formsets for GenericRelations
 * Formsets for ManyToMany relations with intermediate tables
 * Using formsets within CBVs without lots of faffing (properly DRY, you might
   say)
 
The initial work is based on this pull request on the original django-uni-forms:

 * https://github.com/pydanny/django-uni-form/pull/69/files
 
Initially I was a bit pissed that Miguel had rejected the pull until I realised
that it was essentially incomplete.  There was a whole set of work to be done
both in laying out the forms and in saving the results which I've tackled here.
I've chosen to implement it as an extension to `Crispy Forms`_ rather than on
the main package because the code here simply isn't up to the standard required
of a package as widely used as `Crispy Forms`_ yet, and may never be.

I hope, however, that it helps other people who've been struggling with similar
problems.

More documentation to come.
 
.. _Crispy Forms: https://github.com/maraujop/django-crispy-forms
