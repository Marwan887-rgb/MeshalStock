-- MeshalStock Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Drop table if exists (careful - this deletes all data!)
-- DROP TABLE IF EXISTS stock_data;

-- Create stock_data table
CREATE TABLE IF NOT EXISTS stock_data (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    market TEXT NOT NULL CHECK (market IN ('saudi', 'us')),
    date DATE NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate entries
    UNIQUE(symbol, market, date)
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stock_data(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_market ON stock_data(market);
CREATE INDEX IF NOT EXISTS idx_stock_date ON stock_data(date);
CREATE INDEX IF NOT EXISTS idx_stock_symbol_date ON stock_data(symbol, date);
CREATE INDEX IF NOT EXISTS idx_stock_market_date ON stock_data(market, date);

-- Create a composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_stock_symbol_market_date ON stock_data(symbol, market, date DESC);

-- Enable Row Level Security (RLS) for security
ALTER TABLE stock_data ENABLE ROW LEVEL SECURITY;

-- Create policy to allow read access to all users (for API)
CREATE POLICY "Allow public read access" ON stock_data
    FOR SELECT
    USING (true);

-- Create policy to allow insert/update with API key (for data updates)
CREATE POLICY "Allow service role full access" ON stock_data
    FOR ALL
    USING (auth.role() = 'service_role');

-- Create a view for latest stock data (optional - for faster queries)
CREATE OR REPLACE VIEW latest_stock_data AS
SELECT DISTINCT ON (symbol, market)
    symbol,
    market,
    date,
    open,
    high,
    low,
    close,
    volume
FROM stock_data
ORDER BY symbol, market, date DESC;

-- Create index on the view for even faster queries
CREATE INDEX IF NOT EXISTS idx_latest_stock ON stock_data(symbol, market, date DESC);

-- Comments for documentation
COMMENT ON TABLE stock_data IS 'Historical stock price data for Saudi and US markets';
COMMENT ON COLUMN stock_data.symbol IS 'Stock ticker symbol (e.g., AAPL, 2222.SR)';
COMMENT ON COLUMN stock_data.market IS 'Market identifier: saudi or us';
COMMENT ON COLUMN stock_data.date IS 'Trading date';
COMMENT ON COLUMN stock_data.open IS 'Opening price';
COMMENT ON COLUMN stock_data.high IS 'Highest price of the day';
COMMENT ON COLUMN stock_data.low IS 'Lowest price of the day';
COMMENT ON COLUMN stock_data.close IS 'Closing price';
COMMENT ON COLUMN stock_data.volume IS 'Trading volume';

-- Show table info
SELECT 
    'Table created successfully!' as status,
    COUNT(*) as record_count
FROM stock_data;
