---
description: Catalog and inventory pattern for product management and stock tracking
type: pattern
category: domain-model
abstraction: [data, commerce]
---
# Catalog

## Recognition

How to identify this pattern in code.

### Signatures

- `Product`, `Variant`, `SKU` model classes with relationships between them
- `stock`, `inventory`, `quantity_on_hand`, `available_quantity` fields
- `Catalog`, `Category`, `Collection` grouping models for product organization
- `price`, `Price`, `PricingRule` models with currency and amount fields
- `cart`, `Cart`, `CartItem`, `line_item`, `LineItem` for purchase aggregation
- Python: `django-oscar`, `saleor`, `product` app with variant and stock models
- JS/TS: `medusa`, `saleor`, `shopify-api` imports, product/variant types
- Go: product/variant/inventory structs, stock management service
- Rust: commerce domain models with `Sku`, `Variant`, `InventoryLevel`
- Java: `Product` entity with `@OneToMany` variants, `StockLevel` tracking

### Confidence

- **high** -- Product/Variant/SKU hierarchy with inventory tracking, pricing rules, and cart/line-item models forming a complete commerce domain
- **medium** -- Product catalog with categories and variants but inventory managed externally
- **low** -- Simple item list with a price field but no variant, stock, or pricing rule concepts

## Architecture

### When to use
- E-commerce platforms with product listings, variants (size, color), and inventory management
- Marketplace applications with multi-seller catalogs and unified search
- Any system managing a catalog of purchasable items with pricing and availability

### Anti-patterns
- Storing variant attributes as free-form JSON without a defined schema, making queries and validation unreliable
- Stock tracking without concurrency control, allowing overselling under concurrent purchases
- Price calculation scattered across the codebase instead of centralized in a pricing service or rule engine

### Complements
- [search-index](/concepts/search-index) — product catalogs need full-text search with faceted filtering
- [rule-engine](/concepts/rule-engine) — pricing rules and promotions often use rule-based evaluation
- [subscription](/concepts/subscription) — subscription commerce combines catalog with recurring billing

## Impact

Catalog models sit at the center of commerce systems, affecting search, checkout, fulfillment, and analytics. Stock accuracy directly impacts customer experience, and pricing consistency requires centralized rule evaluation. Testing must cover concurrent stock operations, and monitoring should track inventory accuracy and pricing rule evaluation.
