from app import main


class FakeContext:
    def __init__(self) -> None:
        self.aws_request_id = "test-id"


event = {
    "disable_core_logic_crawl": True,
    "force_run_proptrack_crawl": False,
    "force_run_sqm_weekly_rents_crawl": False,
    "force_run_sqm_total_property_stock": False,
    "force_run_sqm_vacancy_rate": False,
    "force_run_quarterly_median_house_sales": False,
    "is_dry_run": True,
    "simulated_date": "2023-08-2"
}

res = main(event, FakeContext())

print("Lambda response:")
print(res)
