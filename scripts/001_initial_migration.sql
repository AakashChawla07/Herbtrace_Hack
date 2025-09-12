-- Initial database setup for HerbTrace
-- This script creates the basic database structure

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create database user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'herbtrace_user') THEN

      CREATE ROLE herbtrace_user LOGIN PASSWORD 'herbtrace_password';
   END IF;
END
$do$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE herbtrace TO herbtrace_user;
GRANT ALL ON SCHEMA public TO herbtrace_user;

-- Create initial herb species data
INSERT INTO traceability_herbspecies (name, scientific_name, sanskrit_name, common_names, medicinal_properties, harvesting_season, quality_parameters, created_at, updated_at) VALUES
('Ashwagandha', 'Withania somnifera', 'Ashvagandha', '["Winter Cherry", "Indian Ginseng"]', '{"adaptogenic": true, "stress_relief": true, "immunity": true}', 'Winter', '{"withanolides": "min 0.3%", "moisture": "max 10%"}', NOW(), NOW()),
('Turmeric', 'Curcuma longa', 'Haridra', '["Haldi", "Golden Spice"]', '{"anti_inflammatory": true, "antioxidant": true, "digestive": true}', 'Post-monsoon', '{"curcumin": "min 3%", "moisture": "max 10%"}', NOW(), NOW()),
('Brahmi', 'Bacopa monnieri', 'Brahmi', '["Water Hyssop", "Thyme-leafed Gratiola"]', '{"cognitive": true, "memory": true, "neuroprotective": true}', 'Throughout year', '{"bacosides": "min 12%", "moisture": "max 10%"}', NOW(), NOW()),
('Neem', 'Azadirachta indica', 'Nimba', '["Margosa", "Indian Lilac"]', '{"antibacterial": true, "antifungal": true, "skin_health": true}', 'Summer', '{"azadirachtin": "min 300ppm", "moisture": "max 8%"}', NOW(), NOW()),
('Amla', 'Phyllanthus emblica', 'Amalaki', '["Indian Gooseberry", "Emblic"]', '{"vitamin_c": true, "antioxidant": true, "immunity": true}', 'Winter', '{"vitamin_c": "min 500mg/100g", "moisture": "max 12%"}', NOW(), NOW());

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_batch_collection_location ON traceability_batch USING GIST (collection_location);
CREATE INDEX IF NOT EXISTS idx_batch_status ON traceability_batch (status);
CREATE INDEX IF NOT EXISTS idx_batch_species ON traceability_batch (species_id);
CREATE INDEX IF NOT EXISTS idx_batch_collector ON traceability_batch (collector_id);
CREATE INDEX IF NOT EXISTS idx_batch_created_at ON traceability_batch (created_at);

CREATE INDEX IF NOT EXISTS idx_processing_event_batch ON traceability_processingevent (batch_id);
CREATE INDEX IF NOT EXISTS idx_processing_event_type ON traceability_processingevent (event_type);
CREATE INDEX IF NOT EXISTS idx_processing_event_date ON traceability_processingevent (event_date);

CREATE INDEX IF NOT EXISTS idx_quality_test_batch ON traceability_qualitytest (batch_id);
CREATE INDEX IF NOT EXISTS idx_quality_test_type ON traceability_qualitytest (test_type);
CREATE INDEX IF NOT EXISTS idx_quality_test_pass_status ON traceability_qualitytest (pass_status);

CREATE INDEX IF NOT EXISTS idx_consumer_verification_batch ON traceability_consumerverification (batch_id);
CREATE INDEX IF NOT EXISTS idx_consumer_verification_date ON traceability_consumerverification (verification_date);

CREATE INDEX IF NOT EXISTS idx_blockchain_transaction_hash ON blockchain_blockchaintransaction (transaction_hash);
CREATE INDEX IF NOT EXISTS idx_blockchain_transaction_batch ON blockchain_blockchaintransaction (batch_id);
CREATE INDEX IF NOT EXISTS idx_blockchain_transaction_status ON blockchain_blockchaintransaction (status);
