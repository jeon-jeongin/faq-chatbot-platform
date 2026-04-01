import argparse
import csv
import html
import json
import re
import requests


CATEGORY_API_URL = "https://faq-editor-api.toss.im/api/v1/categories/?workspace_id=1"
TAG_API_URL = "https://faq-editor-api.toss.im/api/v1/tags/?workspace_id=1"
TOSS_FAQ_BASE_URL = "https://support.toss.im/faq?category="
FAQ_LIST_API_URL = "https://faq-editor-api.toss.im/api/v1/workspaces/1/faq/"
FAQ_DETAIL_API_URL_TEMPLATE = "https://faq-editor-api.toss.im/api/v1/workspaces/1/faq/{faq_id}/"
DEFAULT_ORDER_BY = "-is_pinned,-updated_time,-created_time,-count"


def build_headers():
    # 브라우저와 유사한 User-Agent를 사용해 차단 가능성을 낮춥니다.
    return {"User-Agent": "Mozilla/5.0"}


def get_success_payload(url: str, params: dict | None = None):
    # Toss FAQ API는 공통적으로 {"success": ...} 형태를 반환합니다.
    headers = build_headers()
    res = requests.get(url, headers=headers, params=params, timeout=10)
    res.raise_for_status()
    payload = res.json()
    return payload.get("success", {})


def fetch_categories(api_url: str):
    # 사이드바 카테고리(id/name/priority)를 수집해 크롤링 시작점으로 사용합니다.
    categories = get_success_payload(api_url)

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


def fetch_faq_list_page(category_id: int, page: int = 1, page_size: int = 10):
    # 특정 카테고리의 FAQ 목록을 페이지 단위로 1회 조회합니다.
    params = {
        "page": page,
        "page_size": page_size,
        "category_id": category_id,
        "order_by": DEFAULT_ORDER_BY,
        "with_deleted": "false",
    }
    success = get_success_payload(FAQ_LIST_API_URL, params=params)
    results = success.get("results", [])
    return {
        "count": success.get("count", 0),
        "next": success.get("next"),
        "previous": success.get("previous"),
        "results": results,
    }


def fetch_faq_detail(faq_id: int):
    # 상세 API 확인용 함수입니다. 현재는 목록/상세 응답이 동일한 경우가 많습니다.
    url = FAQ_DETAIL_API_URL_TEMPLATE.format(faq_id=faq_id)
    return get_success_payload(url)


def fetch_tags(api_url: str):
    # tag id를 tag name으로 매핑하기 위한 태그 사전 API입니다.
    return get_success_payload(api_url)


def build_tag_id_name_map(tags: list):
    # 내보내기 단계에서 재사용할 수 있도록 tag 조회 테이블을 생성합니다.
    return {tag.get("id"): tag.get("name", "") for tag in tags if tag.get("id") is not None}


def enrich_row_with_tag_names(row: dict, tag_id_name_map: dict):
    # 원본 row를 유지한 채 tag id 목록에 대응되는 tag 이름 목록을 추가합니다.
    tag_ids = row.get("tag_set", []) or []
    tag_names = [tag_id_name_map.get(tag_id, "") for tag_id in tag_ids]
    return {
        **row,
        "tag_names": tag_names,
    }


def normalize_row_for_export(row: dict, source_category_id: int, tag_id_name_map: dict):
    # CSV 저장에 맞는 스키마로 정규화합니다(HTML 원문 + 텍스트 동시 보관).
    enriched = enrich_row_with_tag_names(row, tag_id_name_map)
    description_html = enriched.get("description", "") or ""
    description_text = html_to_text(description_html)
    return {
        "id": enriched.get("id"),
        "title": enriched.get("title", ""),
        "description_html": description_html,
        "description_text": description_text,
        "updated_time": enriched.get("updated_time"),
        "created_time": enriched.get("created_time"),
        "is_top": enriched.get("is_top"),
        "is_pinned": enriched.get("is_pinned"),
        "workspace_id": enriched.get("workspace_id"),
        "source_category_id": source_category_id,
        "category_set": json.dumps(enriched.get("category_set", []), ensure_ascii=False),
        "tag_set": json.dumps(enriched.get("tag_set", []), ensure_ascii=False),
        "tag_names": json.dumps(enriched.get("tag_names", []), ensure_ascii=False),
        "link": enriched.get("link", ""),
    }


def summarize_faq_row(row: dict):
    # 디버깅 로그에서 빠르게 확인할 수 있도록 한 줄 요약을 만듭니다.
    description = row.get("description", "") or ""
    description_text_preview = html_to_text(description)[:120].replace("\n", " ")
    return (
        f"- id={row.get('id')}, title={row.get('title')}, "
        f"description_text_preview={description_text_preview}"
    )


def html_to_text(raw_html: str):
    # 인덱싱/미리보기를 위한 경량 HTML -> 텍스트 변환입니다.
    text = re.sub(r"<[^>]+>", " ", raw_html or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def crawl_category_all_pages(category_id: int, page_size: int = 10):
    # next=None이 나올 때까지 단일 카테고리를 페이지네이션으로 순회합니다.
    page = 1
    api_count = None
    all_rows = []
    seen_ids = set()
    duplicate_count = 0

    while True:
        page_data = fetch_faq_list_page(category_id=category_id, page=page, page_size=page_size)
        if api_count is None:
            api_count = page_data["count"]

        rows = page_data["results"]
        unique_rows, page_duplicate_count = split_unique_rows(rows, seen_ids)
        duplicate_count += page_duplicate_count
        all_rows.extend(unique_rows)

        print(
            f"page={page}, rows={len(rows)}, page_duplicates={page_duplicate_count}, "
            f"accumulated_unique_rows={len(all_rows)}"
        )

        if page_data["next"] is None:
            break

        page += 1

    return {
        "api_count": api_count or 0,
        "unique_rows": all_rows,
        "unique_count": len(all_rows),
        "duplicate_count": duplicate_count,
        "total_pages": page,
    }


def split_unique_rows(rows: list, seen_ids: set):
    # 단일 카테고리 순회 중 faq id 기준으로 중복을 제거합니다.
    unique_rows = []
    duplicate_count = 0
    for row in rows:
        faq_id = row.get("id")
        if faq_id in seen_ids:
            duplicate_count += 1
            continue
        seen_ids.add(faq_id)
        unique_rows.append(row)
    return unique_rows, duplicate_count


def run_step_1():
    # Step 1: 카테고리 API 연결 및 사이드바 샘플 출력 확인
    print("[STEP 1] category list crawl test")
    category_links = fetch_categories(CATEGORY_API_URL)

    if not category_links:
        print("category links not found")
        return

    print(f"total categories: {len(category_links)}")
    print("sample categories (top 5):")
    for link in category_links[:5]:
        print(
            f"- id={link['id']}, name={link['name']}, priority={link['priority']}, "
            f"absolute_href={link['absolute_href']}"
        )


def run_step_2(category_id: int, page: int, page_size: int):
    # Step 2: 단일 카테고리/단일 페이지 응답 구조 확인
    print("[STEP 2] single category + single page test")
    print(f"request category_id={category_id}, page={page}, page_size={page_size}")

    page_data = fetch_faq_list_page(category_id=category_id, page=page, page_size=page_size)
    results = page_data["results"]

    print(f"api total count for category: {page_data['count']}")
    print(f"next page url exists: {page_data['next'] is not None}")
    print(f"fetched rows in this page: {len(results)}")

    if not results:
        print("no faq rows returned")
        return

    print("sample faq rows (top 3):")
    for row in results[:3]:
        print(summarize_faq_row(row))


def run_step_3(category_id: int, page_size: int):
    # Step 3: 페이지네이션 루프와 count 정합성 확인
    print("[STEP 3] single category pagination full crawl test")
    print(f"request category_id={category_id}, page_size={page_size}")
    result = crawl_category_all_pages(category_id=category_id, page_size=page_size)

    print("-" * 60)
    print(f"total pages crawled: {result['total_pages']}")
    print(f"api count: {result['api_count']}")
    print(f"unique rows crawled: {result['unique_count']}")
    print(f"duplicate rows skipped: {result['duplicate_count']}")
    print(f"count matches: {result['api_count'] == result['unique_count']}")

    if result["unique_rows"]:
        print("sample crawled faq rows (top 3):")
        for row in result["unique_rows"][:3]:
            print(summarize_faq_row(row))


def run_step_4(category_id: int, page_size: int, detail_sample_size: int):
    # Step 4: 샘플 FAQ 기준 목록 응답과 상세 응답 비교
    print("[STEP 4] detail api sample compare test")
    print(
        f"request category_id={category_id}, page_size={page_size}, "
        f"detail_sample_size={detail_sample_size}"
    )

    page_data = fetch_faq_list_page(category_id=category_id, page=1, page_size=page_size)
    list_rows = page_data["results"]

    if not list_rows:
        print("no faq rows returned in list api")
        return

    sample_rows = list_rows[:detail_sample_size]
    print(f"list sample rows selected: {len(sample_rows)}")

    for index, row in enumerate(sample_rows, start=1):
        faq_id = row.get("id")
        if faq_id is None:
            continue

        detail = fetch_faq_detail(faq_id)
        list_keys = set(row.keys())
        detail_keys = set(detail.keys())
        only_in_detail = sorted(detail_keys - list_keys)
        only_in_list = sorted(list_keys - detail_keys)

        list_description = row.get("description", "") or ""
        detail_description = detail.get("description", "") or ""
        description_same = list_description == detail_description
        list_text_preview = html_to_text(list_description)[:160]
        detail_text_preview = html_to_text(detail_description)[:160]

        print("-" * 60)
        print(f"[sample {index}] faq_id={faq_id}")
        print(f"title(list)  : {row.get('title')}")
        print(f"title(detail): {detail.get('title')}")
        print(f"description_same: {description_same}")
        print(f"description_text_preview(list): {list_text_preview}")
        print(f"description_text_preview(detail): {detail_text_preview}")
        print(f"keys_only_in_detail: {only_in_detail}")
        print(f"keys_only_in_list: {only_in_list}")


def run_step_5(category_id: int, page_size: int):
    # Step 5: 샘플 row에서 tag id -> tag name 매핑 확인
    print("[STEP 5] tag_set + tags mapping test")
    print(f"request category_id={category_id}, page_size={page_size}")

    tags = fetch_tags(TAG_API_URL)
    tag_id_name_map = build_tag_id_name_map(tags)
    print(f"total tags fetched: {len(tags)}")
    print(f"tag map size: {len(tag_id_name_map)}")

    page_data = fetch_faq_list_page(category_id=category_id, page=1, page_size=page_size)
    rows = page_data["results"]
    if not rows:
        print("no faq rows returned in list api")
        return

    print(f"faq rows in first page: {len(rows)}")
    print("sample tag mapping rows (top 3):")
    for row in rows[:3]:
        enriched = enrich_row_with_tag_names(row, tag_id_name_map)
        print("-" * 60)
        print(f"faq_id: {enriched.get('id')}")
        print(f"title: {enriched.get('title')}")
        print(f"tag_set(ids): {enriched.get('tag_set', [])}")
        print(f"tag_names: {enriched.get('tag_names', [])}")


def crawl_all_categories(page_size: int, dedupe_by_id: bool = True):
    # 전체 크롤링 경로: 카테고리 -> 페이지네이션 -> 내보내기용 정규화
    categories = fetch_categories(CATEGORY_API_URL)
    tags = fetch_tags(TAG_API_URL)
    tag_id_name_map = build_tag_id_name_map(tags)

    all_rows = []
    seen_ids = set()
    duplicate_id_count = 0

    for category in categories:
        category_id = category["id"]
        category_name = category["name"]
        print(f"[category start] id={category_id}, name={category_name}")
        result = crawl_category_all_pages(category_id=category_id, page_size=page_size)
        print(
            f"[category done] id={category_id}, pages={result['total_pages']}, "
            f"unique_rows={result['unique_count']}, duplicates={result['duplicate_count']}"
        )

        for row in result["unique_rows"]:
            faq_id = row.get("id")
            # 동일 FAQ가 여러 카테고리에 걸릴 수 있어 전역 id 기준으로 중복 제거합니다.
            if dedupe_by_id and faq_id in seen_ids:
                duplicate_id_count += 1
                continue
            if dedupe_by_id:
                seen_ids.add(faq_id)
            all_rows.append(
                normalize_row_for_export(
                    row=row, source_category_id=category_id, tag_id_name_map=tag_id_name_map
                )
            )

    return {
        "rows": all_rows,
        "category_count": len(categories),
        "tag_count": len(tags),
        "duplicate_id_count": duplicate_id_count,
    }


def write_rows_to_csv(output_csv_path: str, rows: list):
    # 스프레드시트에서 한글이 깨지지 않도록 UTF-8 BOM으로 저장합니다.
    if not rows:
        print("no rows to write")
        return

    fieldnames = list(rows[0].keys())
    with open(output_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def validate_rows(rows: list):
    # 임베딩/인덱싱 전 최소 품질 지표를 계산합니다.
    total_rows = len(rows)
    unique_ids = {row.get("id") for row in rows if row.get("id") is not None}
    duplicate_id_count = total_rows - len(unique_ids)
    empty_description_count = sum(
        1 for row in rows if not (row.get("description_text", "") or "").strip()
    )
    return {
        "total_rows": total_rows,
        "unique_id_count": len(unique_ids),
        "duplicate_id_count": duplicate_id_count,
        "empty_description_count": empty_description_count,
    }


def run_step_6(page_size: int, output_csv_path: str, dedupe_by_id: bool):
    # Step 6: 전체 크롤링 후 최종 CSV 저장
    print("[STEP 6] full crawl all categories + save csv")
    print(
        f"request page_size={page_size}, output_csv_path={output_csv_path}, "
        f"dedupe_by_id={dedupe_by_id}"
    )
    result = crawl_all_categories(page_size=page_size, dedupe_by_id=dedupe_by_id)
    rows = result["rows"]
    write_rows_to_csv(output_csv_path=output_csv_path, rows=rows)

    print("-" * 60)
    print(f"categories crawled: {result['category_count']}")
    print(f"tags fetched: {result['tag_count']}")
    print(f"rows saved: {len(rows)}")
    print(f"duplicates skipped by id: {result['duplicate_id_count']}")
    print(f"saved csv path: {output_csv_path}")


def run_step_7(input_csv_path: str):
    # Step 7: 저장된 CSV 기준 사후 품질 점검
    print("[STEP 7] post-crawl data quality check")
    print(f"request input_csv_path={input_csv_path}")

    with open(input_csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    metrics = validate_rows(rows)
    print("-" * 60)
    print(f"total rows: {metrics['total_rows']}")
    print(f"unique id count: {metrics['unique_id_count']}")
    print(f"duplicate id count: {metrics['duplicate_id_count']}")
    print(f"empty description_text count: {metrics['empty_description_count']}")


def build_arg_parser():
    # 단계별 디버깅 흐름을 위한 CLI 옵션을 한 곳에서 정의합니다.
    parser = argparse.ArgumentParser(description="toss faq crawler step test")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4, 5, 6, 7], default=1)
    parser.add_argument("--category-id", type=int, default=5)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=10)
    parser.add_argument("--detail-sample-size", type=int, default=3)
    parser.add_argument("--output-csv", type=str, default="data/toss_faq_data.csv")
    parser.add_argument("--input-csv", type=str, default="data/toss_faq_data.csv")
    parser.add_argument("--no-dedupe-by-id", action="store_true")
    return parser


def execute_step(args):
    # 각 step 내부 로직을 유지한 채 실행 분기만 담당합니다.
    if args.step == 1:
        run_step_1()
        return

    if args.step == 2:
        run_step_2(category_id=args.category_id, page=args.page, page_size=args.page_size)
        return

    if args.step == 3:
        run_step_3(category_id=args.category_id, page_size=args.page_size)
        return

    if args.step == 4:
        run_step_4(
            category_id=args.category_id,
            page_size=args.page_size,
            detail_sample_size=args.detail_sample_size,
        )
        return

    if args.step == 5:
        run_step_5(category_id=args.category_id, page_size=args.page_size)
        return

    if args.step == 6:
        run_step_6(
            page_size=args.page_size,
            output_csv_path=args.output_csv,
            dedupe_by_id=not args.no_dedupe_by_id,
        )
        return

    run_step_7(input_csv_path=args.input_csv)


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    execute_step(args)


if __name__ == "__main__":
    main()
