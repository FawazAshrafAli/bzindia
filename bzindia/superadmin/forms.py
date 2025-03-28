from django import forms
from ckeditor.widgets import CKEditorWidget

from educational.models import MultiPage as CourseMultiPage, CourseDetail
from service.models import MultiPage as ServiceMultiPage, ServiceDetail
from product.models import MultiPage as ProductMultiPage, ProductDetailPage
from registration.models import MultiPage as RegistrationMultiPage, RegistrationDetailPage
from company.models import Company

class CourseMultiPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = CourseMultiPage
        fields = ["description"]


class ServiceMultiPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ServiceMultiPage
        fields = ["description"]


class ProductMultiPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ProductMultiPage
        fields = ["description"]


class RegistrationMultiPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = RegistrationMultiPage
        fields = ["description"]


class CourseDetailDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = CourseDetail
        fields = ["description"]


class ServiceDetailDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ServiceDetail
        fields = ["description"]


class ProductDetailDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ProductDetailPage
        fields = ["description"]


class RegistrationDetailPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = RegistrationDetailPage
        fields = ["description"]


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["description"]