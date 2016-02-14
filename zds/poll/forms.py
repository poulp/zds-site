#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget

from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder

from zds.poll.models import Poll, Choice, UniqueVote, MultipleVote, MULTIPLE_VOTE_KEY, UNIQUE_VOTE_KEY


#############################
# Poll
#############################


class PollForm(forms.ModelForm):

    class Meta:
        model = Poll
        fields = ['title', 'anonymous_vote', 'enddate', 'type_vote']
        widgets = {
            'title': forms.TextInput(attrs={'required': 'required'}),
            'enddate': SelectDateWidget()
        }

    def __init__(self, *args, **kwargs):
        super(PollForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Field('title'),
            Field('anonymous_vote'),
            Field('unique_vote'),
            Field('enddate')
        )

    def clean(self):
        cleaned_data = super(PollForm, self).clean()

        title = cleaned_data.get('title')

        if title and title.strip() == '':
            self._errors['title'] = self.error_class(
                ['Le champ titre ne peut être vide'])
            if 'title' in cleaned_data:
                del cleaned_data['title']

        enddate = cleaned_data.get('enddate')

        if enddate is not None and enddate < datetime.datetime.today():
            self._errors['enddate'] = self.error_class(
                ['La date ne peut pas être antérieure à aujourd\'hui'])
            if 'enddate' in cleaned_data:
                del cleaned_data['enddate']

        return cleaned_data


class UpdatePollForm(forms.ModelForm):

    class Meta:
        model = Poll
        fields = ('activate', 'enddate')
        widgets = {
            'enddate': SelectDateWidget()
        }

    def __init__(self, *args, **kwargs):
        super(UpdatePollForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('enddate'),
            Field('activate'),
            ButtonHolder(
                StrictButton("Editer", type='submit'),
            ),
        )

#############################
# Choices
#############################


class ChoiceForm(forms.ModelForm):

    class Meta:
        model = Choice
        fields = ['choice']

    def clean(self):
        cleaned_data = super(ChoiceForm, self).clean()
        choice = cleaned_data.get('choice')

        if choice and choice.strip() == '':
            self._errors['choice'] = self.error_class(
                ['Le champ choix ne peut être vide'])
            if 'title' in cleaned_data:
                del cleaned_data['choice']

        return cleaned_data


class ChoiceFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ChoiceFormSetHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(
            Field('choice'),
        )
        self.render_required_fields = False
        self.form_tag = False


PollInlineFormSet = forms.inlineformset_factory(
    Poll,
    Choice,
    form=ChoiceForm,
    can_delete=False,
    can_order=False,
    extra=0,
    min_num=2,
    max_num=20
)

#############################
# Votes
#############################


class UniqueVoteForm(forms.ModelForm):

    class Meta:
        model = UniqueVote
        fields = ('choice',)
        widgets = {
            'choice': forms.RadioSelect()
        }

    def __init__(self, poll=None, *args, **kwargs):
        super(UniqueVoteForm, self).__init__(*args, **kwargs)
        self.fields['choice'].empty_label = None
        self.fields['choice'].queryset = Choice.objects.filter(poll=poll)

        if kwargs.get('initial'):
            button_label = 'Modifier mon vote'
        else:
            button_label = 'Voter'

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('choice'),
            ButtonHolder(
                StrictButton(button_label, type='submit')
            )
        )


class MultipleVoteForm(forms.Form):

    choices = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=None,
        required=False
    )

    class Meta:
        model = MultipleVote
        fields = ('choices',)

    def __init__(self, poll=None, *args, **kwargs):
        super(MultipleVoteForm, self).__init__(*args, **kwargs)
        self.fields['choices'].empty_label = None
        self.fields['choices'].queryset = Choice.objects.filter(poll=poll)
        self.helper = FormHelper()

        if kwargs.get('initial'):
            button_label = 'Modifier mon vote'
        else:
            button_label = 'Voter'

        self.helper.layout = Layout(
            'choices',
            ButtonHolder(
                StrictButton(button_label, type='submit'),
            ),
        )


def get_vote_form(poll, data=None, *args, **kwargs):
    if poll.type_vote == MULTIPLE_VOTE_KEY:
        return MultipleVoteForm(poll, data=data, *args, **kwargs)
    elif poll.type_vote == UNIQUE_VOTE_KEY:
        return UniqueVoteForm(poll, data=data, *args, **kwargs)
