from datetime import datetime, timedelta


def generate_dates():
    return [
        (datetime.now() + timedelta(days=i)).strftime("%d.%m %H:%M")
        for i in range(1, 8)
    ]
