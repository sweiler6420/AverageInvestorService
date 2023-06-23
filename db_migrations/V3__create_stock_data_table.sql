--Create stock_data table

create table avg_inv.stock_data (
	stock_id uuid not null,
	"date" date not null,
	"time" time not null,
	open_price numeric(8,2) not null,
	high_price numeric(8,2) not null,
	low_price numeric(8,2) not null,
	close_price numeric(8,2) not null,
	volume bigint not null
);