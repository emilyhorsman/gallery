from django.views.generic.detail import DetailView
from ua_parser import user_agent_parser

from photos.models import Photo


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
