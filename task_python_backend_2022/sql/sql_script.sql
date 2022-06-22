CREATE TABLE domain (
        id INTEGER NOT NULL,
        domain_name VARCHAR(63),
        registred DATETIME,
        unregistred DATETIME,
        PRIMARY KEY (id)
)

CREATE TABLE domain_flag (
        id INTEGER NOT NULL,
        domain_name INTEGER,
        expired BOOLEAN,
        outzone BOOLEAN,
        delete_candidate BOOLEAN,
        PRIMARY KEY (id),
        FOREIGN KEY(domain_name) REFERENCES domain (domain_name)
)

SELECT domain.domain_name, domain_flag.domain_name AS domain_name_1 
FROM domain, domain_flag
WHERE domain.registred = true AND domain_flag.expired = false

SELECT domain_flag.domain_name
FROM domain_flag
WHERE domain_flag.expired = true OR domain_flag.outzone = true
