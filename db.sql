-- =====================================================
-- Autism Screening System Database
-- PostgreSQL
-- =====================================================

-- ==========================
-- Drop Tables
-- ==========================

DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS analysis_results CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS children CASCADE;
DROP TABLE IF EXISTS parents CASCADE;

-- =====================================================
-- Parents Table
-- =====================================================

CREATE TABLE parents (

    id SERIAL PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(100) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,

    phone VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- =====================================================
-- Children Table
-- =====================================================

CREATE TABLE children (

    id SERIAL PRIMARY KEY,

    parent_id INT NOT NULL,

    name VARCHAR(100) NOT NULL,

    age INT NOT NULL,

    gender VARCHAR(10)
        CHECK (gender IN ('male','female')),

    birth_date DATE,

    photo_path TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_parent
        FOREIGN KEY(parent_id)
        REFERENCES parents(id)
        ON DELETE CASCADE

);

-- =====================================================
-- Sessions Table
-- =====================================================

CREATE TABLE sessions (

    id SERIAL PRIMARY KEY,

    child_id INT NOT NULL,

    detection_type VARCHAR(20)
        DEFAULT 'initial'
        CHECK (detection_type IN ('initial','follow_up')),

    frames_folder_path TEXT NOT NULL,

    detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_child
        FOREIGN KEY(child_id)
        REFERENCES children(id)
        ON DELETE CASCADE

);

-- =====================================================
-- Analysis Results Table
-- =====================================================

CREATE TABLE analysis_results (

    id SERIAL PRIMARY KEY,

    session_id INT UNIQUE NOT NULL,

    risk_level VARCHAR(20)
        CHECK (risk_level IN ('low','moderate','high')),

    confidence_score DECIMAL(5,2),

    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_session
        FOREIGN KEY(session_id)
        REFERENCES sessions(id)
        ON DELETE CASCADE

);

-- =====================================================
-- Recommendations Table
-- =====================================================

CREATE TABLE recommendations (

    id SERIAL PRIMARY KEY,

    risk_level VARCHAR(20) NOT NULL
        CHECK (risk_level IN ('low','moderate','high')),

    recommendation_text TEXT NOT NULL

);

-- =====================================================
-- Notifications Table
-- =====================================================

CREATE TABLE notifications (

    id SERIAL PRIMARY KEY,

    parent_id INT NOT NULL,

    title VARCHAR(100) NOT NULL,

    message TEXT NOT NULL,

    is_read BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notification_parent
        FOREIGN KEY(parent_id)
        REFERENCES parents(id)
        ON DELETE CASCADE

);

-- =====================================================
-- Indexes
-- =====================================================

CREATE INDEX idx_children_parent
ON children(parent_id);

CREATE INDEX idx_sessions_child
ON sessions(child_id);

CREATE INDEX idx_analysis_session
ON analysis_results(session_id);

CREATE INDEX idx_recommendations_level
ON recommendations(risk_level);

CREATE INDEX idx_notifications_parent
ON notifications(parent_id);





-- ==========================================
-- Parents
-- ==========================================

INSERT INTO parents (name, email, password, phone)
VALUES
('Ahmed Mostafa', 'ahmed@gmail.com', '123456', '01012345678'),
('Sara El-Sayed', 'sara@gmail.com', '123456', '01112345678'),
('Mohamed Adel', 'mohamed@gmail.com', '123456', '01212345678');

-- ==========================================
-- Children
-- ==========================================

INSERT INTO children
(parent_id, name, age, gender, birth_date, photo_path)
VALUES
(
1,
'Youssef',
5,
'male',
'2021-03-15',
'https://drive.google.com/file/d/1NE44DtE6_gm-sI221uBmz6cbYrdO0gte/view?usp=drive_link'
),

(
1,
'Lina',
2,
'female',
'2023-07-02',
'https://drive.google.com/file/d/1ZusF2I92p6jpBtDihWos9awwAwvgFVdv/view?usp=drive_link'
),

(
2,
'Ahmed',
5,
'male',
'2020-11-20',
'https://drive.google.com/file/d/1KTfWILp8b7v0PpX67SZo8GWJwPCmw0_T/view?usp=drive_link'
),

(
3,
'Alaa',
4,
'female',
'2022-01-09',
'https://drive.google.com/file/d/1fPdAekXeCDuSwBhUEb5oPI84H4vdmApN/view?usp=drive_link'
);

-- ==========================================
-- Sessions
-- ==========================================

INSERT INTO sessions
(child_id, detection_type, frames_folder_path)
VALUES

(1,'initial','frames/youssef/session1'),

(1,'follow_up','frames/youssef/session2'),

(2,'initial','frames/lina/session1'),

(3,'initial','frames/omar/session1'),

(4,'initial','frames/hana/session1');

-- ==========================================
-- Analysis Results
-- ==========================================

INSERT INTO analysis_results
(session_id, risk_level, confidence_score)
VALUES

(1,'moderate',86.20),

(2,'low',91.30),

(3,'high',94.80),

(4,'moderate',88.50),

(5,'low',92.70);

-- ==========================================
-- Recommendations
-- ==========================================

INSERT INTO recommendations
(risk_level, recommendation_text)
VALUES

('low','Occupational Therapy: Enhances daily living skills, fine motor coordination, and sensory integration for functional independence.'),

('low','Speech Therapy: Improves verbal and nonverbal communication, articulation, and language comprehension.'),

('moderate','Applied Behavior Analysis (ABA): Uses data-driven strategies to reinforce positive behaviors and reduce challenging behaviors.'),

('moderate','Sensory Integration Therapy: Helps regulate sensory processing and responses to environmental stimuli.'),

('moderate','Social Skills Training: Develops interpersonal communication, understanding of social cues, and cooperative play.'),

('high','Special Education Programs: Provides structured learning and communication strategies tailored to individual needs.'),

('high','Aquatic Therapy: Supports motor skill development, coordination, and therapeutic movement in a water environment.'),

('high','Art & Music Therapy: Facilitates emotional expression, creativity, and social engagement through creative modalities.');

-- ==========================================
-- Notifications
-- ==========================================

INSERT INTO notifications
(parent_id, title, message)
VALUES

(
1,
'Analysis Ready',
'The autism screening analysis for your child has been completed successfully.'
),

(
2,
'Follow-up Reminder',
'Your child is ready for the next screening session.'
),

(
3,
'New Result',
'The latest analysis results are now available.'
);