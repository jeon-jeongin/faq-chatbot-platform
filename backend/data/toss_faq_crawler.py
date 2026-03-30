import requests


CATEGORY_API_URL = "https://faq-editor-api.toss.im/api/v1/categories/?workspace_id=1"
TOSS_FAQ_BASE_URL = "https://support.toss.im/faq?category="


def fetch_categories(api_url: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(api_url, headers=headers, timeout=10)
    res.raise_for_status()
    res.encoding = res.apparent_encoding or "utf-8"

    payload = res.json()
    categories = payload.get("success", [])

    result = []
    for category in categories:
        category_id = category.get("id")
        if category_id is None:
            continue
        result.append(
            {
                "id": category_id,
                "name": category.get("name", ""),
                "priority": category.get("priority"),
                "href": f"/faq?category={category_id}",
                "absolute_href": f"{TOSS_FAQ_BASE_URL}{category_id}",
            }
        )

    return result


def main():
    print("crawling data")
    category_links = fetch_categories(CATEGORY_API_URL)

    if not category_links:
        print("category links not found")
        return

    for link in category_links:
        print("category id:", link["id"])
        print("category name:", link["name"])
        print("category priority:", link["priority"])
        print("category href:", link["href"])
        print("category absolute_href:", link["absolute_href"])
        print("-" * 40)


if __name__ == "__main__":
    main()
