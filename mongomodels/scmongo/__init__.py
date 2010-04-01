"MongoModels for Svarga framework"

from svarga import forms

class MMSelectMultipleField(forms.SelectMultipleField):
    def __init__(self, label=u'', validators=None, coerce=unicode, choices=None, \
                model=None, *args, **kwargs):

        super(MMSelectMultipleField, self).__init__(self, *args, **kwargs)
        self.model = model
        self.choices = self._choices

    @property
    def _choices(self):
        return ((i.id, self.coerce(i)) for i in self.model.objects.all())

