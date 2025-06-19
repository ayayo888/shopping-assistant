# Page snapshot

```yaml
- main:
  - heading "智能购物意图分析" [level=2]
  - text: 请输入商品链接、名称或描述，系统将自动解析您的购物意图。
  - textbox "例如：https://item.taobao.com/item.htm?id=...": 今天天气怎么样？
  - button "分析意图"
  - heading "识别结果：" [level=4]
  - img "Weather App"
  - img "eye"
  - text: Preview
  - link "Weather App":
    - /url: https://example.com/weather-app
  - text: 价格：¥0
- alert
- button "Open Next.js Dev Tools":
  - img
```