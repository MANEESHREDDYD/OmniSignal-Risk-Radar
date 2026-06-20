from .base_connector import BaseConnector


class DemoIMessageConnector(BaseConnector):
    platform = "imessage"

    def sync(self, account_id: str) -> list[dict]:
        from ...seed_data import get_demo_messages
        return [m for m in get_demo_messages() if m["platform"] == self.platform and m["connected_account_id"] == account_id]

