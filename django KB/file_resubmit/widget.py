import os
import uuid

from django import forms
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.conf import settings
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe

from .cache import FileCache


class ResubmitBaseWidget(ClearableFileInput):
    def __init__(self, attrs=None, field_type=None):
        super(ResubmitBaseWidget, self).__init__(attrs=attrs)
        self.cache_key = ''
        self.field_type = field_type

    def value_from_datadict(self, data, files, name):
        upload = super(ResubmitBaseWidget, self).value_from_datadict(
            data, files, name)
        if upload == FILE_INPUT_CONTRADICTION:
            return upload

        self.input_name = "%s_cache_key" % name
        self.cache_key = data.get(self.input_name, "")

        if name in files:
            self.cache_key = self.random_key()[:10]
            upload = files[name]
            FileCache().set(self.cache_key, upload)
        elif self.cache_key:
            restored = FileCache().get(self.cache_key, name)
            if restored:
                upload = restored
                files[name] = upload
        return upload

    def random_key(self):
        return uuid.uuid4().hex

    def output_extra_data(self, value):
        output = ''
        if value and self.cache_key:
            output += ' ' + self.filename_from_value(value)
        if self.cache_key:
            output += forms.HiddenInput().render(
                self.input_name,
                self.cache_key,
                {},
            )
        return output

    def filename_from_value(self, value):
        if value:
            return os.path.split(value.name)[-1]


class ResubmitFileWidget(ResubmitBaseWidget):
    template_with_initial = getattr(ClearableFileInput, 'template_with_initial', '')
    template_with_clear = getattr(ClearableFileInput, 'template_with_clear', '')

    def render(self, name, value, attrs=None, renderer=None, **kwargs):
        output = ClearableFileInput.render(self, name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class ResubmitImageWidget(ResubmitFileWidget):
    pass


class AdminResubmitImageWidget(AdminResubmitBaseWidget):
    def render(self, name, value, renderer=None, attrs=None):
        output = super(AdminResubmitImageWidget, self).render(
            name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)
    

class ImgPreview(ClearableFileInput):
    """Renamed input button"""
    def render(self, name, value, attrs=None, **kwargs):
        if value == "":
            return f'\
                <p class="file-upload">\
                    <input \
                        type="file" \
                        name="{name}" \
                        accept="image/*" \
                        id="id_{name}" \
                        style="display:none;"\
                    />\
                    <input \
                        type="button" \
                        id="pick_{name}" \
                        value="Alege fisier"\
                    />\
                    <span class="file-upload" id="span_{name}">\
                        &nbsp;&nbsp; Fisier ales: &nbsp;&nbsp;&nbsp;&nbsp;\
                    </span>\
                </p>'
        elif value is not None:
            return f'<img src="{value.url}" width="300" height="300">'
                    
