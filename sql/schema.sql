CREATE TABLE Company (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    company_name CHAR(50) NOT NULL
);

CREATE TABLE Title (
    title_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    title_name CHAR(50) NOT NULL
);

CREATE TABLE Application (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    application_date TEXT NOT NULL,
    offer INTEGER NOT NULL,
    fk_company_id INTEGER NOT NULL,
    fk_title_id INTEGER NOT NULL,
    FOREIGN KEY (fk_company_id) REFERENCES Company(company_id),
    FOREIGN KEY (fk_title_id) REFERENCES Title(title_id)
);

CREATE TABLE Interview (
    interview_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    fk_application_id INTEGER NOT NULL,
    FOREIGN KEY (fk_application_id) REFERENCES Application(application_id)
);


-- -- 插入Company数据
-- INSERT INTO Company (company_name) VALUES
-- ('Company A'),
-- ('Company B'),
-- ('Company C'),
-- ('Company D'),
-- ('Company E'),
-- ('Company F'),
-- ('Company G'),
-- ('Company H'),
-- ('Company I'),
-- ('Company J'),
-- ('Company K'),
-- ('Company L'),
-- ('Company M'),
-- ('Company N'),
-- ('Company O'),
-- ('Company P'),
-- ('Company Q'),
-- ('Company R'),
-- ('Company S'),
-- ('Company T');
--
-- -- 插入Title数据
-- INSERT INTO Title (title_name) VALUES
-- ('Title 1'),
-- ('Title 2'),
-- ('Title 3'),
-- ('Title 4'),
-- ('Title 5'),
-- ('Title 6'),
-- ('Title 7'),
-- ('Title 8'),
-- ('Title 9'),
-- ('Title 10'),
-- ('Title 11'),
-- ('Title 12'),
-- ('Title 13'),
-- ('Title 14'),
-- ('Title 15'),
-- ('Title 16'),
-- ('Title 17'),
-- ('Title 18'),
-- ('Title 19'),
-- ('Title 20');
--
-- -- 插入Application数据
-- INSERT INTO Application (application_date, offer, fk_company_id, fk_title_id) VALUES
-- ('2024-07-01', 0, 1, 1),
-- ('2024-07-02', 1, 2, 2),
-- ('2024-07-03', 0, 3, 3),
-- ('2024-07-04', 1, 4, 4),
-- ('2024-07-05', 0, 5, 5),
-- ('2024-07-06', 1, 6, 6),
-- ('2024-07-07', 0, 7, 7),
-- ('2024-07-08', 1, 8, 8),
-- ('2024-07-09', 0, 9, 9),
-- ('2024-07-10', 1, 10, 10),
-- ('2024-07-11', 0, 11, 11),
-- ('2024-07-12', 1, 12, 12),
-- ('2024-07-13', 0, 13, 13),
-- ('2024-07-14', 1, 14, 14),
-- ('2024-07-15', 0, 15, 15),
-- ('2024-07-16', 1, 16, 16),
-- ('2024-07-17', 0, 17, 17),
-- ('2024-07-18', 1, 18, 18),
-- ('2024-07-19', 0, 19, 19),
-- ('2024-07-20', 1, 20, 20),
-- ('2024-07-21', 0, 1, 1),
-- ('2024-07-22', 1, 2, 2),
-- ('2024-07-23', 0, 3, 3),
-- ('2024-07-24', 1, 4, 4),
-- ('2024-07-25', 0, 5, 5),
-- ('2024-07-26', 1, 6, 6),
-- ('2024-07-27', 0, 7, 7),
-- ('2024-07-28', 1, 8, 8),
-- ('2024-07-29', 0, 9, 9),
-- ('2024-07-30', 1, 10, 10),
-- ('2024-07-31', 0, 11, 11),
-- ('2024-07-32', 1, 12, 12),
-- ('2024-07-33', 0, 13, 13),
-- ('2024-07-34', 1, 14, 14),
-- ('2024-07-35', 0, 15, 15),
-- ('2024-07-36', 1, 16, 16),
-- ('2024-07-37', 0, 17, 17),
-- ('2024-07-38', 1, 18, 18),
-- ('2024-07-39', 0, 19, 19),
-- ('2024-07-40', 1, 20, 20),
-- ('2024-07-41', 0, 1, 1),
-- ('2024-07-42', 1, 2, 2),
-- ('2024-07-43', 0, 3, 3),
-- ('2024-07-44', 1, 4, 4),
-- ('2024-07-45', 0, 5, 5),
-- ('2024-07-46', 1, 6, 6),
-- ('2024-07-47', 0, 7, 7),
-- ('2024-07-48', 1, 8, 8),
-- ('2024-07-49', 0, 9, 9),
-- ('2024-07-50', 1, 10, 10);
--
-- -- 插入Interview数据
-- INSERT INTO Interview (fk_application_id) VALUES
-- (1),
-- (1),
-- (1),
-- (2),
-- (3),
-- (4),
-- (5),
-- (6),
-- (7),
-- (8),
-- (9),
-- (10),
-- (11),
-- (12),
-- (13),
-- (14),
-- (15),
-- (16),
-- (17),
-- (18),
-- (19),
-- (20);
