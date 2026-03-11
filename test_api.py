import requests
import json

url = "https://vplatform.assembly.go.kr/api/api/cms/content/contentList"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://vplatform.assembly.go.kr',
    'Referer': 'https://vplatform.assembly.go.kr/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

def fetch(extra_params, page_size=5):
    payload = {
        "fcltNameList": [], "policyIdList": [],
        "contentType": "PRESSCONF",
        "page": 0, "pageSize": page_size,
        "monaCdList": []
    }
    payload.update(extra_params)
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    items = r.json().get('data', [])
    return [(i.get('cid'), i.get('eventDt','')[:10]) for i in items]

# 첫 번째 아이템의 전체 필드 출력
def print_first_item():
    payload = {
        "fcltNameList": [], "policyIdList": [],
        "contentType": "FULL",
        "page": 0, "pageSize": 1,
        "monaCdList": []
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    items = r.json().get('data', [])
    if items:
        print("\n=== 첫 번째 아이템 전체 필드 ===")
        for k, v in items[0].items():
            print(f"  {k}: {v}")

print_first_item()

# 1. 날짜 범위 필터 시도
print("=== 날짜 범위 파라미터 시도 ===")
tests = [
    {"startDt": "2020-01-01", "endDt": "2020-12-31"},
    {"fromDt": "2020-01-01", "toDt": "2020-12-31"},
    {"startDate": "2020-01-01", "endDate": "2020-12-31"},
    {"searchStartDt": "2020-01-01", "searchEndDt": "2020-12-31"},
    {"eventStartDt": "2020-01-01", "eventEndDt": "2020-12-31"},
    {"year": "2020"},
    {"searchYear": "2020"},
]
base_cids = set(c for c, _ in fetch({}))
print(f"기본 결과 (최신): {list(base_cids)[:3]}")

for params in tests:
    result = fetch(params)
    cids = set(c for c, _ in result)
    different = cids != base_cids
    dates = [d for _, d in result if d]
    print(f"  {list(params.keys())} → {len(result)}건, 기본과 다름={different}, 날짜샘플={dates[:2]}")

# 2. 정렬 파라미터 시도
print("\n=== 정렬/오프셋 파라미터 시도 ===")
sort_tests = [
    {"sortType": "ASC"},
    {"sortType": "asc"},
    {"orderBy": "ASC"},
    {"sort": "eventDt,asc"},
    {"offset": 500},
    {"start": 500},
    {"startIndex": 500},
    {"skip": 500},
]
for params in sort_tests:
    result = fetch(params)
    cids = set(c for c, _ in result)
    different = cids != base_cids
    print(f"  {params} → {len(result)}건, 기본과 다름={different}")
