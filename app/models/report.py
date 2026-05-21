class Report:
    def generate_report(self):
        from app.models.item import Item
        items = Item.query.all()
        return {
            "total": len(items),
            "items": [item.to_dict() for item in items if hasattr(item, 'to_dict')],
            "by_status": self.count_by_status(),
            "expired": self.list_expired()
        }

    def count_by_status(self):
        from app.models.item import Item
        from app import db
        items = Item.query.all()
        status_counts = {
            "Found": 0,
            "UnderReview": 0,
            "Claimed": 0,
            "Returned": 0,
            "Disputed": 0,
            "Expired": 0
        }
        for item in items:
            if hasattr(item, 'status') and item.status in status_counts:
                status_counts[item.status] += 1
        return status_counts

    def list_expired(self):
        from app.models.item import Item
        items = Item.query.all()
        expired = []
        for item in items:
            if hasattr(item, 'is_expired') and item.is_expired():
                expired.append(item)
        return expired
