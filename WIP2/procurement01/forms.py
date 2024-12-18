from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import SKU, Company, RFP, GeneralQuestion, RFP_SKUs, SKUSpecificQuestion, GeneralQuestionResponse, SKUSpecificQuestionResponse

import json

class LoginForm(AuthenticationForm):
    pass


class SKUForm(forms.ModelForm):
    class Meta:
        model = SKU
        fields = ['name', 'sku_code', 'image_url']  # All the fields you want to show



class SupplierForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'email']  # Include the email field
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Supplier Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Supplier Email'}),
        }

    def save(self, procurer, *args, **kwargs):
        supplier = super(SupplierForm, self).save(commit=False)
        supplier.company_type = 'Supplier'
        supplier.procurer = procurer
        supplier.save()
        return supplier

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email is required for suppliers.')
        return email



class RFPBasicForm(forms.ModelForm):
    class Meta:
        model = RFP
        fields = ['title', 'description']  # Ensure general_info_files is included here
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter RFP Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter RFP Description'}),
        }


class RFP_SKUForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, label="Quantity")
    target_price = forms.DecimalField(decimal_places=2, max_digits=10, label="Target Price")
    unit_size = forms.CharField(max_length=100, label="Unit Size")
    
    class Meta:
        model = RFP_SKUs
        fields = ['sku', 'quantity', 'target_price', 'unit_size']

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields['sku'].queryset = SKU.objects.filter(company=company)




class RFPForm(forms.ModelForm):
    additional_columns = forms.CharField(widget=forms.HiddenInput(), required=False)  # Hidden field for custom columns

    class Meta:
        model = RFP
        fields = ['title', 'description']

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Save additional columns as JSON if provided
        if 'additional_columns' in self.cleaned_data:
            instance.additional_columns = json.dumps(self.cleaned_data['additional_columns'])
        if commit:
            instance.save()
        return instance


class SKUSearchForm(forms.Form):
    query = forms.CharField(label='Search SKUs', max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Search for SKUs...',
        'class': 'form-control'
    }))



class GeneralQuestionForm(forms.ModelForm):
    class Meta:
        model = GeneralQuestion
        fields = ['question_text', 'question_type', 'multiple_choice_options']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-control question-type-select'}),
            # Optionally, define the widget for 'multiple_choice_options' if needed
        }

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get("question_type")
        multiple_choice_options = cleaned_data.get("multiple_choice_options")

        if question_type in ['Single-select', 'Multi-select'] and not multiple_choice_options:
            self.add_error('multiple_choice_options', 'This field is required for single or multi-select questions.')

        # No further transformation is necessary here since JavaScript now sends the data as a comma-separated string
        return cleaned_data



class SKUSpecificQuestionForm(forms.ModelForm):
    class Meta:
        model = SKUSpecificQuestion
        fields = ['question', 'question_type']
        labels = {
            'question': 'Question',
            'question_type': 'Question Type'
        }
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'Enter question text', 'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SKUSpecificQuestionForm, self).__init__(*args, **kwargs)
        # Customize the question_type choices display
        self.fields['question_type'].choices = SKUSpecificQuestion.QUESTION_TYPES




class GeneralQuestionResponseForm(forms.ModelForm):
    class Meta:
        model = GeneralQuestionResponse
        fields = ['answer_text', 'answer_choice', 'answer_number', 'answer_date', 'answer_file']

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)  # Expecting the question instance to be passed in
        super().__init__(*args, **kwargs)

        # Customize the form fields based on question type
        if question:
            self.fields['answer_text'].widget = forms.HiddenInput()
            self.fields['answer_choice'].widget = forms.HiddenInput()
            self.fields['answer_number'].widget = forms.HiddenInput()
            self.fields['answer_date'].widget = forms.HiddenInput()
            self.fields['answer_file'].widget = forms.HiddenInput()

            if question.question_type == 'text':
                self.fields['answer_text'].widget = forms.Textarea(attrs={'placeholder': 'Enter your answer here'})
                self.fields['answer_text'].required = True
            elif question.question_type in ['Single-select', 'Multi-select']:
                choices = [(option, option) for option in question.multiple_choice_options.split(',')]
                if question.question_type == 'Single-select':
                    self.fields['answer_choice'] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect)
                else:
                    self.fields['answer_choice'] = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
                self.fields['answer_choice'].required = True
            elif question.question_type == 'number':
                self.fields['answer_number'].widget = forms.NumberInput(attrs={'placeholder': 'Enter a number'})
                self.fields['answer_number'].required = True
            elif question.question_type == 'date':
                self.fields['answer_date'].widget = forms.DateInput(attrs={'type': 'date'})
                self.fields['answer_date'].required = True
            elif question.question_type == 'file':
                self.fields['answer_file'].widget = forms.FileInput()
                self.fields['answer_file'].required = True


class SKUSpecificQuestionResponseForm(forms.ModelForm):
    class Meta:
        model = SKUSpecificQuestionResponse
        fields = ['answer_text', 'answer_number', 'answer_file', 'answer_date']

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)  # Expecting the question instance to be passed in
        super().__init__(*args, **kwargs)

        # Customize the form fields based on question type
        if question:
            self.fields['answer_text'].widget = forms.HiddenInput()
            self.fields['answer_number'].widget = forms.HiddenInput()
            self.fields['answer_date'].widget = forms.HiddenInput()
            self.fields['answer_file'].widget = forms.HiddenInput()

            if question.question_type == 'text':
                self.fields['answer_text'].widget = forms.Textarea(attrs={'placeholder': 'Enter your answer here'})
                self.fields['answer_text'].required = True
            elif question.question_type == 'number':
                self.fields['answer_number'].widget = forms.NumberInput(attrs={'placeholder': 'Enter a number'})
                self.fields['answer_number'].required = True
            elif question.question_type == 'date':
                self.fields['answer_date'].widget = forms.DateInput(attrs={'type': 'date'})
                self.fields['answer_date'].required = True
            elif question.question_type == 'file':
                self.fields['answer_file'].widget = forms.FileInput()
                self.fields['answer_file'].required = True
