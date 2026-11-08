"""Conceptual names and curated associations, grounded in the existing SQL model."""
from layered_core_content import group, leaf
from diagram_content import link

CONCEPTS = {
 'public.t_key':('Key material',['# id','key_name','effective_at / expired_at']),
 'consent.m_consent_type':('Consent type',['# id','name / is_required']),
 'consent.t_consent':('Consent version',['# id / code','consent_type_id','consent_version / body']),
 'authen.m_user':('User',['# id','username / email_address','display_name']),
 'authen.t_user_consent':('Consent acknowledgement',['# id','user_id / consent_id','result / is_read']),
 'authen.m_user_password':('Password credential',['# id / user_id','row_type','password / password_salt']),
 'authen.t_user_reset_password':('Password reset request',['# id / user_id','reset_token','expired_at']),
 'authen.l_user_referral':('Referral event',['# id / user_id','referrer_id?']),
 'authen.m_user_information':('User profile',['# id / user_id','phone_number / date_of_birth','gender']),
 'authen.t_user_address':('Delivery address',['# id / user_id','address / city / postal_code','is_default']),
 'authen.t_user_access_token':('Access token',['# id / user_id','session_id / token','expired_at']),
 'authen.t_user_refresh_token':('Refresh token',['# id / user_id','session_id / token','expired_at']),
 'authen.l_user_login_attempt':('Login attempt',['# id / user_id?','identifier_hash','result']),
 'author.m_role':('Role',['# id / name','description']),
 'author.m_permission':('Permission',['# id / name','description']),
 'author.m_scope':('Scope',['# id / scope','name / description']),
 'author.t_permission_scope':('Scoped permission',['# id / permission_id','scope_id']),
 'author.t_role_permission':('Role permission grant',['# id / role_id','permission_id']),
 'author.t_role_permission_scope':('Scoped role grant',['# id / role_permission_id','permission_scope_id']),
 'author.t_user_role':('User role assignment',['# id / user_id','role_id']),
 'author.t_user_permission':('Direct permission grant',['# id / user_id','permission_id','permission_scope_id?']),
 'product.m_product_type':('Product type',['# id / name','description']),
 'product.m_product_category':('Category',['# id / parent_id?','name / slug']),
 'product.m_product_category_attribute':('Category attribute definition',['# id / category_id','name']),
 'product.m_product_brand':('Brand',['# id / name','description']),
 'product.m_product':('Product',['# id / name','type_id / category_id / brand_id','slug / body']),
 'product.m_product_attribute':('Product attribute value',['# id / product_id','attribute_id / value']),
 'product.m_product_image':('Product image',['# id / product_id','option_value_id?','image_path']),
 'product.m_product_sku':('Product SKU',['# id / product_id','name / combination_key']),
 'product.m_product_option':('Option level',['# id / product_id','name / level_no']),
 'product.m_product_option_value':('Option value',['# id / option_id','value / sort_order']),
 'product.m_product_sku_option_value':('SKU option selection',['# id / sku_id','option_value_id']),
 'shop.m_shop_type':('Shop type',['# id / name','description']),
 'shop.m_shop':('Shop',['# id / type_id','platform_margin_rate','shop_margin_rate']),
 'shop.t_shop_user':('Shop membership',['# id / shop_id','user_id / role']),
 'shop.m_shop_image':('Shop image',['# id / shop_id','type / seq / image_path']),
 'shop.t_shop_product':('Shop listing',['# id / shop_id','product_id']),
 'shop.t_shop_product_sku':('Shop SKU',['# id / shop_product_id','sku_id / code']),
 'shop.t_shop_product_sku_lot':('Stock lot',['# id / shop_product_sku_id','cost_price / selling_price','quantity / is_on_sale']),
 'shop.t_shop_product_review':('Product review',['# id / shop_product_id','user_id / rating','comment?']),
 'cart.t_cart':('Cart line',['# id / user_id / shop_id','product_id / sku_id','quantity > 0']),
 'sales.t_order':('Order',['# id / user_id / shop_id','address_id + ship_* snapshot','total_price / total_discount / total_tax','total_shipping / total_amount','status / expires_at']),
 'sales.t_order_item':('Order line',['# id / order_id','shop_id / product_id / sku_id','lot_id / quantity','price / discount / total_price','gross_profit / profit shares']),
 'payment.t_payment':('Payment attempt',['# id / order_id','provider_payment_id / status','amount / currency / refund IDs']),
 'shipping.t_shipping':('Shipment',['# id / order_id','status / carrier / tracking','shipped_at / delivered_at']),
 'shipping.t_shipping_item':('Shipment allocation',['# id / shipping_id','order_item_id','quantity > 0']),
 'shipping.t_shipping_stop':('Shipment stop',['# id / shipping_id','stop_number / stop_type','location_name']),
 'campaign.m_campaign':('Campaign',['# id / name','start_at / end_at']),
 'campaign.m_campaign_budget':('Campaign budget',['# id / campaign_id','budget / remaining']),
 'campaign.m_campaign_budget_ledger':('Budget movement',['# id / campaign_budget_id','campaign_id / order_id','entry_type / usage / remaining']),
 'campaign.t_campaign_product':('Product/category target',['# id / campaign_id','product_id?','product_category_id? (XOR)']),
 'campaign.t_campaign_shop':('Shop eligibility',['# id / campaign_id','shop_id']),
 'campaign.t_campaign_discount':('Discount rule',['# id / campaign_id','discount_type / discount_value']),
}

def entity(table,parent,x,y,w=208,h=112,kind='backend'):
 title,fields=CONCEPTS[table]
 n=leaf(parent,table,x,y,w,h,title,table,[(v,True)for v in fields],kind)
 n['table']=table
 return n

def association(parent,child,column,points):
 e=link(parent,child,points);e.update(kind='reference',fk=dict(child=child,column=column,parent=parent));return e

def frame(slug,title,schemas,containers,nodes,edges,notes):
 return dict(slug=slug,title=title,type='ER',schemas=schemas,
  eyebrow='E-COMMERCE / DATABASE-GROUNDED CONCEPTUAL DOMAIN MODEL',
  subtitle='Named entities inside schema groups. Selected associations show all-row cardinality, not request order or aggregate ownership.',
  desc=title+' with business concepts, selected attributes and database-evidenced relationships grouped by SQL schema.',
  containers=containers,nodes=nodes,edges=edges,notes=notes,
  source='Source: db/migrations/up + doc/schema | 53 tables / 11 schemas / 75 FK columns | Full references in companion Markdown',
  legend=[('box','Entity / association entity'),('text','Line = selected FK association'),('text','1 or 0..1 at parent end'),('text','0..* = historical children'),('focal','Editorial focus; not aggregate root')])

def identity():
 nodes=[]
 layout=[('m_user',64,216),('m_user_password',320,216),('t_user_reset_password',536,216),('m_user_information',64,416),('t_user_address',320,416),('t_user_consent',536,416),('t_user_access_token',64,616),('t_user_refresh_token',320,616),('l_user_login_attempt',536,616),('l_user_referral',64,816)]
 for key,x,y in layout:nodes.append(entity('authen.'+key,'identity',x,y,208 if x==64 else 192,kind='focal'if key=='m_user'else'backend'))
 for key,x,y in [('m_role',816,216),('t_role_permission',1064,216),('m_permission',1312,216),('t_user_role',816,416),('t_role_permission_scope',1064,416),('t_permission_scope',1312,416),('t_user_permission',816,616),('m_scope',1064,616)]:nodes.append(entity('author.'+key,'authorization',x,y))
 nodes.extend([entity('consent.m_consent_type','consent',808,840,192),entity('consent.t_consent','consent',1040,840,216),entity('public.t_key','keys',1316,840,212)])
 a=association
 edges=[a('authen.m_user','authen.m_user_password','user_id',[(272,248),(320,248)]),a('authen.m_user','authen.m_user_information','user_id',[(144,328),(144,416)]),a('authen.m_user','authen.t_user_reset_password','user_id',[(240,328),(240,360),(632,360),(632,328)]),a('authen.m_user','authen.t_user_address','user_id',[(208,328),(208,384),(416,384),(416,416)]),a('author.m_role','author.t_role_permission','role_id',[(1024,272),(1064,272)]),a('author.m_permission','author.t_role_permission','permission_id',[(1312,304),(1272,304)]),a('author.m_permission','author.t_permission_scope','permission_id',[(1416,328),(1416,416)]),a('author.t_role_permission','author.t_role_permission_scope','role_permission_id',[(1168,328),(1168,416)]),a('author.t_permission_scope','author.t_role_permission_scope','permission_scope_id',[(1312,472),(1272,472)]),a('author.m_role','author.t_user_role','role_id',[(920,328),(920,416)]),a('author.t_permission_scope','author.t_user_permission','permission_scope_id',[(1488,528),(1488,584),(920,584),(920,616)]),a('consent.m_consent_type','consent.t_consent','consent_type_id',[(1000,896),(1040,896)])]
 return frame('domain-identity-model','Identity, access & consent concepts',['authen','author','consent','public'],[group('identity',40,160,712,828,'Identity & account evidence','authen · 10 tables'),group('authorization',792,160,752,584,'Authorization policy','author · 8 tables'),group('consent',792,784,480,204,'Consent publication','consent · 2 tables'),group('keys',1300,784,244,204,'Key material','public · TECHNICAL SUPPORT')],nodes,edges,[(320,842,'Sessions are correlated by session_id.',10,'body'),(320,862,'There is no Session table or token-to-token FK.',10,'body'),(320,902,'Active uniqueness is a filtered subset;',10,'body'),(320,922,'history still uses 0..* cardinality.',10,'body'),(40,1012,'21 tables. Selected 12 / 23 FK associations; every FK is listed in the companion. No secret values are shown.',11,'body')])

def merchandising():
 nodes=[]
 for key,x,y in [('m_product_category',64,216),('m_product',376,216),('m_product_brand',688,216),('m_product_category_attribute',64,416),('m_product_sku',376,416),('m_product_type',688,416),('m_product_attribute',64,616),('m_product_sku_option_value',376,616),('m_product_image',688,616),('m_product_option',64,816),('m_product_option_value',376,816)]:nodes.append(entity('product.'+key,'catalog',x,y,272,kind='focal'if key=='m_product'else'backend'))
 for key,x,y in [('m_shop_type',1048,216),('m_shop',1312,216),('t_shop_user',1048,416),('m_shop_image',1312,416),('t_shop_product',1048,616),('t_shop_product_sku',1312,616),('t_shop_product_review',1048,816),('t_shop_product_sku_lot',1312,816)]:nodes.append(entity('shop.'+key,'shops',x,y))
 a=association
 edges=[a('product.m_product_category','product.m_product','category_id',[(336,272),(376,272)]),a('product.m_product_option_value','product.m_product_image','option_value_id',[(648,872),(668,872),(668,672),(688,672)]),a('product.m_product_type','product.m_product','type_id',[(688,472),(668,472),(668,360),(584,360),(584,328)]),a('product.m_product','product.m_product_sku','product_id',[(448,328),(448,416)]),a('product.m_product_sku','product.m_product_sku_option_value','sku_id',[(512,528),(512,616)]),a('product.m_product_option_value','product.m_product_sku_option_value','option_value_id',[(584,816),(584,728)]),a('product.m_product_option','product.m_product_option_value','option_id',[(336,872),(376,872)]),a('shop.m_shop_type','shop.m_shop','type_id',[(1256,272),(1312,272)]),a('shop.m_shop','shop.t_shop_product','shop_id',[(1312,304),(1288,304),(1288,592),(1152,592),(1152,616)]),a('shop.t_shop_product','shop.t_shop_product_sku','shop_product_id',[(1256,672),(1312,672)]),a('shop.t_shop_product_sku','shop.t_shop_product_sku_lot','shop_product_sku_id',[(1416,728),(1416,816)]),a('shop.t_shop_product','shop.t_shop_product_review','shop_product_id',[(1152,728),(1152,816)])]
 return frame('domain-merchandising-model','Catalog, shop listings & stock concepts',['product','shop'],[group('catalog',40,160,944,828,'Global product catalog','product · 11 tables'),group('shops',1024,160,520,828,'Merchant offer & inventory','shop · 8 tables')],nodes,edges,[(688,850,'Product SKU is not a shop offer.',10,'body'),(688,870,'A shop offer has stock lots and prices.',10,'body'),(688,910,'One ACTIVE on-sale lot per shop SKU;',10,'body'),(688,930,'older or off-sale lots still exist.',10,'body'),(40,1012,'19 tables. Selected 12 / 25 FK associations. Same-product, SKU and option consistency needs additional domain validation.',11,'body')])

def commerce():
 nodes=[entity('cart.t_cart','cart',64,216,432,128),entity('sales.t_order','sales',64,472,432,144,'focal'),entity('sales.t_order_item','sales',64,720,432,144),entity('payment.t_payment','payment',584,216,416,128),entity('shipping.t_shipping','shipping',584,472,416,112),entity('shipping.t_shipping_item','shipping',584,656,192,112),entity('shipping.t_shipping_stop','shipping',808,656,192,112)]
 for key,x,y in [('m_campaign',1088,216),('m_campaign_budget',1320,216),('t_campaign_discount',1088,416),('m_campaign_budget_ledger',1320,416),('t_campaign_product',1088,616),('t_campaign_shop',1320,616)]:nodes.append(entity('campaign.'+key,'campaign',x,y,192 if x==1088 else 208))
 a=association
 edges=[a('sales.t_order','sales.t_order_item','order_id',[(280,616),(280,720)]),a('sales.t_order','payment.t_payment','order_id',[(496,512),(536,512),(536,280),(584,280)]),a('sales.t_order','shipping.t_shipping','order_id',[(496,552),(584,552)]),a('sales.t_order_item','shipping.t_shipping_item','order_item_id',[(496,736),(584,736)]),a('shipping.t_shipping','shipping.t_shipping_item','shipping_id',[(680,584),(680,656)]),a('shipping.t_shipping','shipping.t_shipping_stop','shipping_id',[(904,584),(904,656)]),a('campaign.m_campaign','campaign.m_campaign_budget','campaign_id',[(1280,272),(1320,272)]),a('campaign.m_campaign','campaign.t_campaign_discount','campaign_id',[(1192,328),(1192,416)]),a('campaign.m_campaign_budget','campaign.m_campaign_budget_ledger','campaign_budget_id',[(1424,328),(1424,416)]),a('campaign.m_campaign','campaign.t_campaign_product','campaign_id',[(1088,280),(1052,280),(1052,672),(1088,672)]),a('campaign.m_campaign','campaign.t_campaign_shop','campaign_id',[(1280,304),(1308,304),(1308,672),(1320,672)])]
 return frame('domain-commerce-model','Cart, orders, money & fulfilment concepts',['cart','sales','payment','shipping','campaign'],[group('cart',40,160,480,208,'Customer selection','cart · 1 table; no cart header'),group('sales',40,416,480,572,'Order & snapshots','sales · 2 tables'),group('payment',560,160,464,208,'Financial attempts','payment · 1 table'),group('shipping',560,416,464,572,'Parcel fulfilment','shipping · 3 tables'),group('campaign',1064,160,480,828,'Promotion & budget accounting','campaign · 6 tables')],nodes,edges,[(64,914,'Order total = price - discount + tax + shipping.',10,'body'),(64,938,'Item total_price = price x quantity (before discount).',10,'body'),(584,826,'Payment history is 0..* per order.',10,'body'),(584,850,'Only a live filtered subset is limited to one.',10,'body'),(584,898,'Shipment allocation supports split quantities;',10,'body'),(584,922,'the FK does not enforce shipment quantity sums.',10,'body'),(1088,814,'Budget movement: RESERVE / RELEASE.',10,'body'),(1088,838,'One entry per budget + order + type.',10,'body'),(1088,886,'Eligibility chooses product XOR category.',10,'body'),(1088,910,'Tax formula and rounding are not in DDL.',10,'body'),(40,1012,'13 tables. Selected 11 / 27 FK associations. Cart -> order is a use-case conversion, not a persisted FK relation.',11,'body')])

def overview():
 groups=[group('access',40,160,456,828,'Identity & governance','21 TABLES · 4 SCHEMAS'),group('merch',536,160,464,828,'Merchandising','19 TABLES · 2 SCHEMAS'),group('trade',1040,160,504,828,'Commerce','13 TABLES · 5 SCHEMAS')]
 specs=[('identity','access',64,216,408,128,'Identity','authen · 10 tables',['User / credential / reset request','Profile / addresses / tokens / account evidence']),('authorization','access',64,392,408,128,'Authorization','author · 8 tables',['Roles / permissions / scopes','Role and direct scoped grants']),('consent','access',64,568,408,128,'Consent','consent · 2 tables',['Consent type + published version','User acknowledgement stays in authen']),('keys','access',64,744,408,128,'Key material','public · 1 technical-support table',['Key name + binary material + effective period','Not a business aggregate']),('catalog','merch',560,216,416,176,'Product catalog','product · 11 tables',['Type / category / brand / product','Attributes / options / values / SKU selections','Shared product definition; no shop stock']),('offers','merch',560,472,416,176,'Merchant offers & inventory','shop · 8 tables',['Shop / membership / images / listing','Shop SKU / stock lot / review','Lot owns selling price, cost and quantity']),('cart','trade',1064,216,456,104,'Cart selection','cart · 1 table',['Cart line per customer + shop + product + SKU']),('orders','trade',1064,360,456,112,'Order & snapshot','sales · 2 tables',['Order + order line; address and price snapshots','Lot reference + order totals + expiry']),('payments','trade',1064,512,456,104,'Payment attempts','payment · 1 table',['Provider identity / amount / status / refund data']),('shipping','trade',1064,656,456,104,'Parcel fulfilment','shipping · 3 tables',['Shipment / allocation / stop; split quantities']),('campaign','trade',1064,800,456,112,'Campaign & budget','campaign · 6 tables',['Eligibility / discount / budget / movement ledger','Budget movement links promotion and order'])]
 nodes=[leaf(parent,key,x,y,w,h,title,tag,[(v,False)for v in lines],'focal'if key=='orders'else'backend')for key,parent,x,y,w,h,title,tag,lines in specs]
 d=frame('domain-model','E-commerce domain map from the database',[],groups,nodes,[],[(560,730,'Read the three detail sheets for all 53 entities.',11,'body'),(560,762,'Names are business interpretations of SQL evidence.',10,'body'),(560,786,'Schema grouping is not a proven DDD context,',10,'body'),(560,810,'aggregate, microservice or transaction boundary.',10,'body'),(560,858,'No Domain service methods are invented from FKs.',10,'body'),(560,882,'Rule candidates and missing guards are explained',10,'body'),(560,906,'in the companion, with source constraints.',10,'body'),(40,1012,'Coverage: 53 / 53 tables and 75 / 75 FK columns in detail-page traceability. This overview is a navigation map.',11,'body')])
 d['type']='Nested';d['subtitle']='Business concept families and selected cross-schema references; all 53 tables are expanded in the three conceptual ER detail sheets.'
 def family_ref(a,b,child,column,parent,points):
  e=link(a,b,points);e.update(kind='reference',fk=dict(child=child,column=column,parent=parent));return e
 d['edges']=[
  family_ref('identity','authorization','author.t_user_role','user_id','authen.m_user',[(268,344),(268,392)]),
  family_ref('consent','identity','authen.t_user_consent','consent_id','consent.t_consent',[(64,632),(52,632),(52,280),(64,280)]),
  family_ref('catalog','offers','shop.t_shop_product','product_id','product.m_product',[(768,392),(768,472)]),
  family_ref('offers','orders','sales.t_order','shop_id','shop.m_shop',[(976,552),(1012,552),(1012,448),(1064,448)]),
  family_ref('orders','payments','payment.t_payment','order_id','sales.t_order',[(1296,472),(1296,512)]),
  family_ref('orders','shipping','shipping.t_shipping','order_id','sales.t_order',[(1520,440),(1540,440),(1540,704),(1520,704)]),
  family_ref('orders','campaign','campaign.m_campaign_budget_ledger','order_id','sales.t_order',[(1520,400),(1556,400),(1556,856),(1520,856)]),
 ]
 d['legend']=[('box','Business concept family'),('text','Line = selected cross-schema FK'),('focal','Order focus; no aggregate claim'),('text','Groups = reading boundaries'),('text','Technical support kept separate')];return d

def views():return [overview(),identity(),merchandising(),commerce()]
