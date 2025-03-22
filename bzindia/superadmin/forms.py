from django import forms
from ckeditor.widgets import CKEditorWidget

from educational.models import MultiPage as CourseMultiPage, CourseDetail

class CourseMultiPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = CourseMultiPage
        fields = ["description"]


class CourseDetailDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = CourseDetail
        fields = ["description"]