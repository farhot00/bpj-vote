from django.views.generic import ListView
class TitleMixin:
    title = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

class FormTitleMixin:
    form_title = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        return context

class GenericListView(ListView):
    template_name = 'generic_list.html'  # Path to the generic template
    model = None  # You can set this dynamically in the URL or a specific view

    def get_queryset(self):
        if self.model is not None:
            return self.model.objects.all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the model fields to the template context
        context['fields'] = self.model._meta.fields
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context
