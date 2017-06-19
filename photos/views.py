from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.shortcuts import redirect
from ua_parser import user_agent_parser

from photos.forms import PhotoForm
from photos.models import Photo, PhotoFile


class PhotoDetailView(DetailView):
    model = Photo

    def get_context_data(self, **kwargs):
        context = super(PhotoDetailView, self).get_context_data(**kwargs)
        context['srcset'] = context['photo'].get_srcset(kwargs['user_agent'])
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(
            object=self.object,
            user_agent=user_agent_parser.ParseUserAgent(request.META['HTTP_USER_AGENT'])
        )
        return self.render_to_response(context)


class PhotoCreateView(FormView):
    template_name = 'photos/photo_create.html'
    form_class = PhotoForm

    def get_success_url(self):
        return reverse(
            'photo-detail',
            kwargs=dict(pk=self.photo.pk),
        )

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form)

        self.photo = form.save()
        PhotoFile.objects.create(
            photo=self.photo,
            is_original=True,
            file=form.cleaned_data['file'],
        )
        if self.request.is_ajax():
            return HttpResponse()
        else:
            return redirect(self.get_success_url())
