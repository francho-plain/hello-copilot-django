-- Create cats table
CREATE TABLE IF NOT EXISTS cats (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    breed VARCHAR(100),
    age INTEGER,
    color VARCHAR(50),
    weight DECIMAL(4,2),
    is_neutered BOOLEAN DEFAULT FALSE,
    owner_name VARCHAR(100),
    adoption_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert random cat data (15 cats)
INSERT INTO cats (name, breed, age, color, weight, is_neutered, owner_name, adoption_date, description) VALUES
('Whiskers', 'Persian', 3, 'White', 4.2, TRUE, 'John Smith', '2023-01-15', 'A fluffy and calm cat who loves to sleep in sunny spots'),
('Shadow', 'Maine Coon', 5, 'Black', 6.8, TRUE, 'Emma Johnson', '2022-08-22', 'Large and friendly cat with a magnificent tail'),
('Luna', 'Siamese', 2, 'Cream', 3.5, FALSE, 'Carlos Rodriguez', '2023-05-10', 'Vocal and intelligent cat who follows her owner everywhere'),
('Milo', 'British Shorthair', 4, 'Gray', 5.1, TRUE, 'Sarah Connor', '2021-12-03', 'Round-faced gentleman with a calm temperament'),
('Bella', 'Ragdoll', 1, 'Blue Point', 3.8, FALSE, 'Mike Wilson', '2023-09-18', 'Young and playful with beautiful blue eyes'),
('Tiger', 'Bengal', 6, 'Golden Spotted', 5.5, TRUE, 'Lisa Anderson', '2020-11-30', 'Active and athletic cat with wild markings'),
('Smokey', 'Russian Blue', 3, 'Blue-Gray', 4.0, TRUE, 'David Lee', '2022-03-14', 'Shy but affectionate with a plush silver coat'),
('Princess', 'Himalayan', 7, 'Chocolate Point', 4.7, TRUE, 'Maria Garcia', '2019-06-25', 'Dignified and calm with long, silky fur'),
('Ginger', 'Scottish Fold', 2, 'Orange Tabby', 3.2, FALSE, 'Tom Brown', '2023-07-08', 'Sweet-natured with distinctive folded ears'),
('Midnight', 'Bombay', 4, 'Jet Black', 4.5, TRUE, 'Anna Taylor', '2021-10-12', 'Sleek black panther-like appearance with golden eyes'),
('Patches', 'Calico', 5, 'Tri-color', 3.9, TRUE, 'Robert Davis', '2020-04-17', 'Independent calico with unique patch patterns'),
('Snowball', 'Turkish Angora', 3, 'Pure White', 3.6, FALSE, 'Jennifer White', '2022-12-05', 'Elegant white cat with heterochromatic eyes'),
('Rusty', 'Abyssinian', 2, 'Ruddy', 4.1, FALSE, 'Chris Martin', '2023-02-28', 'Energetic and curious with a ticked coat pattern'),
('Duchess', 'Norwegian Forest Cat', 6, 'Silver Tabby', 6.2, TRUE, 'Helen Clark', '2020-09-14', 'Majestic long-haired cat with excellent hunting skills'),
('Biscuit', 'Munchkin', 4, 'Cream and White', 3.4, TRUE, 'Kevin Park', '2021-07-20', 'Short-legged sweetheart with a big personality');

-- Create an index for better query performance
CREATE INDEX IF NOT EXISTS idx_cats_breed ON cats(breed);
CREATE INDEX IF NOT EXISTS idx_cats_name ON cats(name);

-- Display confirmation message
SELECT 'Cats table created successfully with ' || COUNT(*) || ' records' AS status FROM cats;