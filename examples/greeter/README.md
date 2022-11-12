# Greeter Example

```bash
# launch example (bali < 3.4)
python main.py --http

# launch example (bali >= 3.4, bali-cli >= 2.5)
python main.py run --http 
bali run http  # Short command with bali-cli

# make a http request
curl http://127.0.0.1:8000/greeters/1

{
  "content": "hello, ID is 1"
}
```
