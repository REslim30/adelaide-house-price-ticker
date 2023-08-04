from app import main

class FakeContext:
   def __init__(self) -> None:
      self.aws_request_id = "test-id"

event = {
   "disable_core_logic_crawl": True,
   "force_run_proptrack_crawl": False,
   "force_run_sqm_research_crawl": True,
   "test_tweet": True,
}

res = main(event, FakeContext())

print("Lambda response:")
print(res)