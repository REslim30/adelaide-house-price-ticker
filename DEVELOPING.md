
Can use this to test:
```shell
aws lambda invoke --function-name adelaide-house-price-ticker --invocation-type Event --cli-binary-format raw-in-base64-out --payload '{"name": "Bob"}' response.json
```