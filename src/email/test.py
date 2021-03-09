from datetime import datetime
from dateutil import parser
from dateutil import tz

if __name__ == '__main__':
    expAtUtcStr = "2021-03-09T03:27:29.059Z"
    # expAtUtcStr = "2021-03-08T03:57:17.884Z"
    format = "%Y-%m-%dT%H:%M:%S.%fZ"

    # expAtUtcStr = "2021-03-08T03:57:17Z"
    # format = "%Y-%m-%dT%H:%M:%SZ"
    expAtUtc = parser.isoparse(expAtUtcStr)
    print(expAtUtc)
    now = datetime.now(tz.UTC)
    print(now)
    # if exp before now
    print(expAtUtc < now)
