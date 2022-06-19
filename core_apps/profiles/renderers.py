import json
from rest_framework.renderers import JSONRenderer


class ProfileJSONRenderer(JSONRenderer):
    """
    Renderer which produces JSON serialized objects.
    """
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context.get('response').status_code
        errors = data.get('errors', None)

        if errors is not None:
            return super().render(data)

        return json.dumps({'status_code': status_code, 'profile': data})


class ProfilesJSONRenderer(JSONRenderer):
    """
    Renderer which produces JSON serialized objects.
    """
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context.get('response').status_code
        errors = data.get('errors', None)

        if errors is not None:
            return super().render(data)

        return json.dumps({'status_code': status_code, 'profiles': data})