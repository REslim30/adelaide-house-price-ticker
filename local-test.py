from app import main

class FakeContext:
   def __init__(self) -> None:
      self.aws_request_id = "test-id"

res = main(None, FakeContext())

print("Lambda response:")
print(res)