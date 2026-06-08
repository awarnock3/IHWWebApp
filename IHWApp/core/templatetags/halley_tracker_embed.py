from django import template

try:
    from halley_tracker.django_template_tags import halley_tracker_html
except ImportError:
    halley_tracker_html = None

register = template.Library()


@register.simple_tag
def halley_tracker_embed(cached_only=False):
    if halley_tracker_html is None:
        return '<section class="halley-tracker"><p>Halley Tracker unavailable</p></section>'
    return halley_tracker_html(cached_only=cached_only)
