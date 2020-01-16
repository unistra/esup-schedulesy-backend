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
        return {**{"code": "too_much_events",
                   "detail": f'Excedeed limit of {settings.ADE_MAX_EVENTS} events'},
                **self.message}
