--add isin to stock table

alter table avg_inv.stocks 
add column isin varchar(12);