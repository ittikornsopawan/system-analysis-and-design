# Database schema

53 tables in 11 schemas, generated from `db/migrations/up/*.sql` using [`template.md`](template.md). ER diagram: [`er-diagram.drawio`](../../db/er-diagram.drawio).


## public

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [t_key](public/t_key.md) | Transaction | 10 | 0 |

## consent

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [m_consent_type](consent/m_consent_type.md) | Master | 9 | 0 |
| [t_consent](consent/t_consent.md) | Transaction | 15 | 1 |

## authen

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [m_user](authen/m_user.md) | Master | 12 | 0 |
| [t_user_consent](authen/t_user_consent.md) | Transaction | 12 | 2 |
| [m_user_password](authen/m_user_password.md) | Master | 10 | 1 |
| [t_user_reset_password](authen/t_user_reset_password.md) | Transaction | 9 | 1 |
| [l_user_referral](authen/l_user_referral.md) | Log | 5 | 2 |
| [m_user_information](authen/m_user_information.md) | Master | 11 | 1 |
| [t_user_address](authen/t_user_address.md) | Transaction | 14 | 1 |
| [t_user_access_token](authen/t_user_access_token.md) | Transaction | 10 | 1 |
| [t_user_refresh_token](authen/t_user_refresh_token.md) | Transaction | 10 | 1 |
| [l_user_login_attempt](authen/l_user_login_attempt.md) | Log | 6 | 1 |

## author

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [m_role](author/m_role.md) | Master | 8 | 0 |
| [m_permission](author/m_permission.md) | Master | 8 | 0 |
| [m_scope](author/m_scope.md) | Master | 9 | 0 |
| [t_permission_scope](author/t_permission_scope.md) | Transaction | 8 | 2 |
| [t_role_permission](author/t_role_permission.md) | Transaction | 8 | 2 |
| [t_role_permission_scope](author/t_role_permission_scope.md) | Transaction | 8 | 2 |
| [t_user_role](author/t_user_role.md) | Transaction | 8 | 2 |
| [t_user_permission](author/t_user_permission.md) | Transaction | 8 | 2 |

## product

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [m_product_type](product/m_product_type.md) | Master | 8 | 0 |
| [m_product_category](product/m_product_category.md) | Master | 10 | 1 |
| [m_product_category_attribute](product/m_product_category_attribute.md) | Master | 9 | 1 |
| [m_product_brand](product/m_product_brand.md) | Master | 8 | 0 |
| [m_product](product/m_product.md) | Master | 13 | 3 |
| [m_product_attribute](product/m_product_attribute.md) | Master | 9 | 2 |
| [m_product_image](product/m_product_image.md) | Master | 9 | 2 |
| [m_product_sku](product/m_product_sku.md) | Master | 10 | 1 |
| [m_product_option](product/m_product_option.md) | Master | 9 | 1 |
| [m_product_option_value](product/m_product_option_value.md) | Master | 9 | 1 |
| [m_product_sku_option_value](product/m_product_sku_option_value.md) | Master | 8 | 2 |

## shop

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [m_shop_type](shop/m_shop_type.md) | Master | 8 | 0 |
| [m_shop](shop/m_shop.md) | Master | 11 | 1 |
| [t_shop_user](shop/t_shop_user.md) | Transaction | 9 | 2 |
| [m_shop_image](shop/m_shop_image.md) | Master | 10 | 1 |
| [t_shop_product](shop/t_shop_product.md) | Transaction | 8 | 2 |
| [t_shop_product_sku](shop/t_shop_product_sku.md) | Transaction | 11 | 2 |
| [t_shop_product_sku_lot](shop/t_shop_product_sku_lot.md) | Transaction | 15 | 1 |
| [t_shop_product_review](shop/t_shop_product_review.md) | Transaction | 10 | 2 |

## cart

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [t_cart](cart/t_cart.md) | Transaction | 11 | 4 |

## sales

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [t_order](sales/t_order.md) | Transaction | 23 | 3 |
| [t_order_item](sales/t_order_item.md) | Transaction | 18 | 5 |

## payment

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [t_payment](payment/t_payment.md) | Transaction | 23 | 1 |

## shipping

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [t_shipping](shipping/t_shipping.md) | Transaction | 13 | 1 |
| [t_shipping_item](shipping/t_shipping_item.md) | Transaction | 9 | 2 |
| [t_shipping_stop](shipping/t_shipping_stop.md) | Transaction | 12 | 1 |

## campaign

| Table | Type | Columns | FKs |
| ----- | ---- | ------: | --: |
| [m_campaign_budget](campaign/m_campaign_budget.md) | Master | 9 | 1 |
| [m_campaign_budget_ledger](campaign/m_campaign_budget_ledger.md) | Master | 13 | 3 |
| [m_campaign](campaign/m_campaign.md) | Master | 10 | 0 |
| [t_campaign_product](campaign/t_campaign_product.md) | Transaction | 9 | 3 |
| [t_campaign_shop](campaign/t_campaign_shop.md) | Transaction | 8 | 2 |
| [t_campaign_discount](campaign/t_campaign_discount.md) | Transaction | 9 | 1 |
