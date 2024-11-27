from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, Role


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.values(
            "id", "title", "description", "creation_date", "rating", "type"
        ).annotate(
            genres=ArrayAgg("genres__name", distinct=True),
            actors=ArrayAgg(
                "persons__full_name",
                filter=Q(personfilmwork__role=Role.ACTOR),
                distinct=True,
            ),
            directors=ArrayAgg(
                "persons__full_name",
                filter=Q(personfilmwork__role=Role.DIRECTOR),
                distinct=True,
            ),
            writers=ArrayAgg(
                "persons__full_name",
                filter=Q(personfilmwork__role=Role.WRITER),
                distinct=True,
            ),
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        queryset_size = len(queryset)
        page_size = self.get_paginate_by(queryset)

        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(
                queryset, page_size
            )
            context = {
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "prev": None,
                "next": None,
            }
            if page.has_previous():
                context["prev"] = page.previous_page_number()
            if page.has_next():
                context["next"] = page.next_page_number()
        else:
            context = {
                "count": queryset_size,
            }

        context["results"] = list(queryset)
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return dict(self.object)
