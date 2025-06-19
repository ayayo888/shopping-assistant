"use client";

import { useIntentStore } from "@/stores/useIntentStore";
import {
  Button,
  Card,
  Form,
  Input,
  Typography,
  Space,
  Spin,
  Alert,
  Image,
} from "antd";
import type { Product } from "@/types";

const { TextArea } = Input;
const { Title, Text, Link } = Typography;

const ProductCard = ({ product }: { product: Product }) => (
  <Card
    hoverable
    style={{ width: 300 }}
    cover={<Image alt={product.title} src={product.image} width={300} height={300} style={{ objectFit: 'cover' }} />}
    data-testid={`product-card-${product.id}`}
  >
    <Card.Meta
      title={<Link href={product.url} target="_blank" rel="noopener noreferrer">{product.title}</Link>}
      description={`价格：¥${product.price}`}
    />
  </Card>
);


export const IntentInputForm = () => {
  const {
    userInput,
    products,
    isLoading,
    error,
    setUserInput,
    parseIntent,
    clearError,
  } = useIntentStore();

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setUserInput(e.target.value);
    if (error) {
      clearError();
    }
  };

  const handleSubmit = () => {
    if (!userInput.trim()) return;
    parseIntent(userInput);
  };

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="large" data-testid="intent-form">
      <Title level={2}>智能购物意图分析</Title>
      <Text>请输入商品链接、名称或描述，系统将自动解析您的购物意图。</Text>
      
      <Spin spinning={isLoading} tip="正在分析意图...">
        <Card>
          <Space direction="vertical" style={{ width: "100%" }}>
            <TextArea
              value={userInput}
              onChange={handleInputChange}
              placeholder="例如：https://item.taobao.com/item.htm?id=..."
              rows={4}
              data-testid="user-input"
            />
            <Button
              type="primary"
              onClick={handleSubmit}
              disabled={isLoading || !userInput.trim()}
              data-testid="submit-button"
            >
              分析意图
            </Button>
          </Space>
        </Card>
      </Spin>

      {error && (
         <Alert
          message="错误"
          description={error}
          type="error"
          showIcon
          closable
          onClose={clearError}
          data-testid="error-message"
        />
      )}

      {products.length > 0 && (
         <div data-testid="product-list">
          <Title level={4}>识别结果：</Title>
           <Space wrap size="large">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </Space>
         </div>
      )}

      {products.length === 0 && !isLoading && !error && userInput && (
          <div data-testid="no-product-message">
              <Text>未识别到明确的购物意图。</Text>
          </div>
      )}
    </Space>
  );
}; 