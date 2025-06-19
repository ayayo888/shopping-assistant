# Page snapshot

```yaml
- main:
  - heading "智能购物意图分析" [level=2]
  - text: 请输入商品链接、名称或描述，系统将自动解析您的购物意图。
  - textbox "例如：https://item.taobao.com/item.htm?id=...": https://item.taobao.com/item.htm?id=12345
  - button "分析意图"
  - heading "识别结果：" [level=4]
  - img "Example Product"
  - img "eye"
  - text: Preview
  - link "Example Product":
    - /url: https://item.taobao.com/item.htm?id=12345
  - text: 价格：¥19.99
- alert
- button "Open Next.js Dev Tools":
  - img
```