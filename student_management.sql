-- --------------------------------------------------------
-- DATABASE: student_management
-- --------------------------------------------------------
CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- --------------------------------------------------------
-- TABLE: students
-- --------------------------------------------------------
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(255),
    program VARCHAR(100),
    semester VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- TABLE: subjects
-- --------------------------------------------------------
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    credits INT DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- TABLE: enrollments
-- --------------------------------------------------------
CREATE TABLE enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    enrollment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- --------------------------------------------------------
-- TABLE: marks
-- --------------------------------------------------------
CREATE TABLE marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    marks_obtained FLOAT DEFAULT 0,
    total_marks FLOAT DEFAULT 100,
    exam_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- --------------------------------------------------------
-- TABLE: attendance
-- --------------------------------------------------------
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent') DEFAULT 'Absent',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- --------------------------------------------------------
-- SAMPLE DATA (Optional)
-- --------------------------------------------------------
INSERT INTO subjects (code, name, credits) VALUES
('CS101', 'Introduction to Programming', 4),
('CS102', 'Data Structures', 4),
('CS103', 'Database Systems', 3);

INSERT INTO students (student_id, first_name, last_name, email, phone, address, program, semester) VALUES
('S001', 'Krish', 'Pednekar', 'krish@example.com', '9876543210', 'Goa, India', 'B.Tech Computer Engg', '5'),
('S002', 'Aarav', 'Mehta', 'aarav@example.com', '9876500001', 'Mumbai, India', 'B.Tech Computer Engg', '5');
