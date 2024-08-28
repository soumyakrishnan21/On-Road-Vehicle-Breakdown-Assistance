from django import template

register = template.Library()

@register.filter
def default_receiver(receiver):
    return receiver if receiver else "Everyone"
