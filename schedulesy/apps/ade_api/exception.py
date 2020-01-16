from django.conf import settings

class ExceptionFactory(object):
    def create_from_xml(self, xml_element):
        msg = xml_element.attrib['trace']
        return (Exception(msg))

    def raise_from_xml(self, xml_element):
        exc = self.create_from_xml(xml_element)
        raise (exc)


class TooMuchEventsError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def context(self):
        return {"error": "too much events",
                "limit": settings.ADE_MAX_EVENTS,
                "resources": self.message}