-- Make ticker_symbol unique
ALTER TABLE avg_inv.stocks ADD CONSTRAINT stocks_un UNIQUE (ticker_symbol);