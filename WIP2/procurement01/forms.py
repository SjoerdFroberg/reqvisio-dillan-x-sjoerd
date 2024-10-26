from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import SKU, Company, RFP, GeneralQuestion, RFP_SKUs
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
        fields = ['name']  # Only the name field is required for now

    def save(self, procurer, *args, **kwargs):
        # Automatically set the company type to 'Supplier' and assign the procurer
        supplier = super(SupplierForm, self).save(commit=False)
        supplier.company_type = 'Supplier'
        supplier.procurer = procurer
        supplier.save()
        return supplier
    



class RFPBasicForm(forms.ModelForm):
    class Meta:
        model = RFP
        fields = ['title', 'description']  # Only show title and description in Step 1



class RFP_SKUForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, label="Quantity")
    target_price = forms.DecimalField(decimal_places=2, max_digits=10, label="Target Price")
    unit_size = forms.CharField(max_length=100, label="Unit Size")
    
    class Meta:
        model = RFP_SKUs
        fields = ['sku', 'quantity', 'target_price', 'unit_size']

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)  # Pass company if needed
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

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get("question_type")
        multiple_choice_options = cleaned_data.get("multiple_choice_options")

        if question_type in ['Single-select', 'Multi-select'] and not multiple_choice_options:
            self.add_error('multiple_choice_options', 'This field is required for single or multi-select questions.')

        # No further transformation is necessary here since JavaScript now sends the data as a comma-separated string
        return cleaned_data
