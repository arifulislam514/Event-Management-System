from django.db.models.signals import post_save, pre_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from events.models import Event
from django.conf import settings
from django.contrib.auth.models import User


@receiver(m2m_changed, sender=Event.participants.through)
def notify_participant_on_participate_event(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        print(instance, instance.participants.all())

        users = User.objects.filter(pk__in=pk_set)
        subject = "New event booked"
        message = f"You have booked to this event: {instance.name}"
        
        for user in users:
            try:
                send_mail(subject,message,settings.EMAIL_HOST_USER,[user.email])
            except Exception as e:
                print(f"Failed to send email to {user.email}: {str(e)}")
