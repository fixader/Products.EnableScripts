## Script (Python): enable XML / ElementTree first.
from xml.etree.ElementTree import fromstring, tostring

root = fromstring('<orders><order id="42">RestrictedPythonExtensions</order></orders>')
order = root.find("order")
return "%s: %s - %s" % (order.tag, order.get("id"), order.text)
