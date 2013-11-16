from django import template

register = template.Library()

@register.filter
def status_bootstrap(value):
    if value == 'CRITICAL':
        return 'danger'
    elif value == 'MAJOR':
        return 'danger'
    elif value == 'MINOR':
        return 'warning'
    elif value == 'WARNING':
        return 'warning'
    elif value == 'CLEARED':
        return success
    elif value == 'INFORMATION':
        return 'info'
    elif value == 'True':
        return 'success'
    elif value == 'False':
        return 'danger'
    elif value:
        return 'success'
    else:
        return 'danger'
