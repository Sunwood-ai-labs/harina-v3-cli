# 📸 Harina v3 CLI - 使用例とサンプル

このフォルダには、Harina v3 CLIの実際の使用例とサンプルファイルが含まれています。

## 🧾 サンプルレシート

`receipt-sample/` フォルダには以下のサンプルが含まれています：

- `IMG_8923.jpg` - コンビニレシートのサンプル
- `IMG_8924.jpg` - スーパーマーケットレシートのサンプル  
- `IMG_8925.jpg` - レストランレシートのサンプル
- `IMG_8926.jpg` - 薬局レシートのサンプル
- `IMG_8927.jpg` - その他のレシートサンプル

各画像に対応するXML出力例も含まれています（`.xml`ファイル）。

## 🚀 サンプルの実行方法

### 基本的な使用方法

```bash
# メインディレクトリから実行
harina example/receipt-sample/IMG_8923.jpg

# 出力ファイルを指定
harina example/receipt-sample/IMG_8923.jpg -o my_output.xml

# 詳細ログを表示
harina example/receipt-sample/IMG_8923.jpg -v
```

### 異なるAIモデルでのテスト

```bash
# Gemini Pro を使用
harina example/receipt-sample/IMG_8924.jpg --model gemini/gemini-1.5-pro

# OpenAI GPT-4o を使用（OPENAI_API_KEYが必要）
harina example/receipt-sample/IMG_8925.jpg --model gpt-4o

# Claude 3 Sonnet を使用（ANTHROPIC_API_KEYが必要）
harina example/receipt-sample/IMG_8926.jpg --model claude-3-sonnet-20240229
```

## 📊 期待される出力例

各サンプル画像を処理すると、以下のような構造化されたXMLが出力されます：

```xml
<?xml version="1.0" ?>
<receipt>
  <store_info>
    <n>店舗名</n>
    <address>住所</address>
    <phone>電話番号</phone>
  </store_info>
  <transaction_info>
    <date>2024-01-15</date>
    <time>14:30</time>
    <receipt_number>12345</receipt_number>
  </transaction_info>
  <items>
    <item>
      <n>商品名</n>
      <quantity>1</quantity>
      <unit_price>100</unit_price>
      <total_price>100</total_price>
    </item>
  </items>
  <totals>
    <subtotal>500</subtotal>
    <tax>50</tax>
    <total>550</total>
  </totals>
</receipt>
```

## 🔧 トラブルシューティング

### よくある問題

1. **APIキーエラー**
   ```bash
   # .envファイルが正しく設定されているか確認
   cat .env
   ```

2. **画像が認識されない**
   - 画像が鮮明で、レシート全体が写っているか確認
   - サポートされている画像形式（JPEG, PNG等）を使用

3. **XMLの出力が不完全**
   - より高精度なモデル（gemini-1.5-pro）を試す
   - 画像の品質を向上させる

## 📖 詳細情報

詳細な使用方法やAPI設定については、[メインREADME](../README.md)を参照してください。

## 🤝 フィードバック

サンプルの追加や改善提案がありましたら、Issueを作成してください。