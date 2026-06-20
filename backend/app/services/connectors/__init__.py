from .demo_calendar_connector import DemoCalendarConnector
from .demo_gmail_connector import DemoGmailConnector
from .demo_imessage_connector import DemoIMessageConnector
from .demo_outlook_connector import DemoOutlookConnector
from .demo_sms_connector import DemoSmsConnector

CONNECTORS = {
    "gmail": DemoGmailConnector(),
    "outlook": DemoOutlookConnector(),
    "sms": DemoSmsConnector(),
    "imessage": DemoIMessageConnector(),
    "calendar": DemoCalendarConnector(),
}

