from .utils import send_invitation_email


class SendInvitationEmailMixin:
    def form_valid(self, form):
        response = super().form_valid(form)
        send_invitation_email(self.request, self.object)
        return response
