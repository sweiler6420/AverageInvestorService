-- Link stock id fk to stock id in the stocks table
ALTER TABLE avg_inv.stock_data
ADD CONSTRAINT stock_id_fk FOREIGN KEY ("stock_id") REFERENCES avg_inv.stocks("stock_id");