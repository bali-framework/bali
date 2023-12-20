# Greeter Example

```bash
# launch example (bali-core < 3.4)
python main.py --http

# launch example (bali-core >= 3.4, bali-core-cli >= 2.5)
python main.py run --http 
bali-core run http  # Short command with bali-core-cli

# make a http request
curl http://127.0.0.1:8000/greeters/1

{
  "content": "hello, ID is 1"
}
```
