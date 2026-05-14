from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from formtools.wizard.views import SessionWizardView

from apps.core.viewmixins import AllowedRolesMixin
from apps.core.viewmixins import HtmxFormSuccessMixin
from apps.core.viewmixins import HtmxTemplateMixin
from apps.users.enums import UserRole

from .filters import PatientFilter
from .forms import QUESTIONNAIRE_FORMS
from .forms import STEP_TITLES
from .forms import PatientCreateForm
from .forms import PatientUpdateForm
from .models import Patient
from .models import QuestionnaireResponse


# ---------------------------------------------------------------------------
# Patient views
# ---------------------------------------------------------------------------
class PatientListView(AllowedRolesMixin, HtmxTemplateMixin, FilterView):
    model = Patient
    filterset_class = PatientFilter
    allowed_roles = [UserRole.ADMIN, UserRole.SPECIALIST, UserRole.PARENT]
    template_name = "patients/patient_list.html"
    htmx_template_name = "#patient-table"
    context_object_name = "patients"
    paginate_by = 20

    def get_queryset(self):
        qs = Patient.objects.with_relations().order_by("-created")
        user = self.request.user
        if user.role == UserRole.SPECIALIST:
            return qs.filter(specialist=user)
        if user.role == UserRole.PARENT:
            return qs.filter(parent=user)
        return qs


class PatientDetailView(AllowedRolesMixin, DetailView):
    model = Patient
    allowed_roles = [UserRole.ADMIN, UserRole.SPECIALIST, UserRole.PARENT]
    template_name = "patients/patient_detail.html"
    context_object_name = "patient"

    def get_queryset(self):
        qs = Patient.objects.with_relations()
        user = self.request.user
        if user.role == UserRole.SPECIALIST:
            return qs.filter(specialist=user)
        if user.role == UserRole.PARENT:
            return qs.filter(parent=user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["responses"] = self.object.questionnaire_responses.order_by("-created")[
            :10
        ]
        return context


class PatientCreateView(AllowedRolesMixin, SuccessMessageMixin, CreateView):
    model = Patient
    form_class = PatientCreateForm
    allowed_roles = [UserRole.ADMIN, UserRole.SPECIALIST]
    template_name = "patients/patient_create.html"
    success_message = _("Patient created successfully.")

    def get_success_url(self):
        return reverse_lazy("patients:patient_detail", kwargs={"pk": self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        parent_pk = self.request.GET.get("parent")
        if parent_pk:
            initial["parent"] = parent_pk
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.role == UserRole.SPECIALIST:
            form.fields.pop("specialist", None)
        return form

    def form_valid(self, form):
        if self.request.user.role == UserRole.SPECIALIST:
            form.instance.specialist = self.request.user
        return super().form_valid(form)


class PatientUpdateView(
    AllowedRolesMixin,
    HtmxTemplateMixin,
    HtmxFormSuccessMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Patient
    form_class = PatientUpdateForm
    allowed_roles = [UserRole.ADMIN, UserRole.SPECIALIST]
    template_name = "patients/patient_update.html"
    htmx_template_name = "#update-form"
    success_message = _("Patient updated successfully.")

    def get_queryset(self):
        qs = Patient.objects.with_relations()
        user = self.request.user
        if user.role == UserRole.SPECIALIST:
            return qs.filter(specialist=user)
        return qs

    def get_success_url(self):
        return reverse_lazy("patients:patient_detail", kwargs={"pk": self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.role == UserRole.SPECIALIST:
            form.fields.pop("specialist", None)
        return form


# ---------------------------------------------------------------------------
# Questionnaire wizard
# ---------------------------------------------------------------------------
class QuestionnaireWizardView(AllowedRolesMixin, SessionWizardView):
    template_name = "patients/questionnaire_wizard.html"
    form_list = QUESTIONNAIRE_FORMS
    allowed_roles = [UserRole.PARENT, UserRole.SPECIALIST]

    def dispatch(self, request, *args, **kwargs):
        from django.db.models import Q
        user = request.user
        condition = Q(parent=user) if user.role == UserRole.PARENT else Q(specialist=user)
        
        self.patient = get_object_or_404(
            Patient,
            Q(pk=self.kwargs["patient_pk"]) & condition,
            is_active=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        current_step = self.steps.current
        context.update(
            {
                "page_title": _("Sleep questionnaire"),
                "patient": self.patient,
                "step_titles_list": list(STEP_TITLES.values()),
                "current_step_title": STEP_TITLES.get(current_step, ""),
            }
        )
        return context

    def done(self, form_list, **kwargs):
        user = self.request.user
        parent = user if user.role == UserRole.PARENT else None
        professional = user if user.role == UserRole.SPECIALIST else None
        
        QuestionnaireResponse.objects.create(
            patient=self.patient,
            parent=parent,
            professional=professional,
            **self.get_all_cleaned_data(),
        )
        messages.success(self.request, _("Questionnaire submitted successfully."))
        return redirect(reverse_lazy("dashboard:index"))
