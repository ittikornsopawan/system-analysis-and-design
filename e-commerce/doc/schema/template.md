---
name: "Schema doc template"
description: "Template of a schema doc (one table: columns, keys, constraints and indexes); read it before you write or regenerate a file under e-commerce/doc/schema."
---

# Table: <table-name>

Description: <table-description>

## Columns

| Key          | Reference   | Column Name   | Data Type   | Length   | Is Nullable   | Description   | Example   |
| ------------ | ----------- | ------------- | ----------- | -------- | ------------- | ------------- | --------- |
| <PK, FK, UQ> | <reference> | <column-name> | <data-type> | <length> | <TRUE, FALSE> | <description> | <example> |

## Constain

| Key Name                              | Column Name        | Description   |
| ------------------------------------- | ------------------ | ------------- |
| <pk,fk,uq,idx>_<table-name>_<columns> | <column>, <column> | <description> |

---

```SQL
CREATE TABLE IF NOT EXISTS <table-name>
(
    ...
);
```
