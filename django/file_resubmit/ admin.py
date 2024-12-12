
class AdminResubmitMixin(object):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, (ImageField, models.ImageField)):
            return db_field.formfield(widget=AdminResubmitImageWidget)
        elif isinstance(db_field, models.FileField):
            return db_field.formfield(widget=AdminResubmitFileWidget)
        else:
            return super(AdminResubmitMixin, self).formfield_for_dbfield(
                db_field, **kwargs)
            