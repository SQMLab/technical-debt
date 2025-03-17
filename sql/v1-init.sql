DROP TABLE IF EXISTS repository;
CREATE TABLE repository
(
    id                    BIGSERIAL PRIMARY KEY,
    project_id            BIGINT UNIQUE NOT NULL,               -- Unique GitHub Repository ID
    name                  VARCHAR(255)  NOT NULL,               -- Repository Name
    full_name             VARCHAR(255)  NOT NULL,               -- Full name (owner/repo)
    is_fork               BOOLEAN       NOT NULL DEFAULT FALSE, -- Whether the repo is a fork or not
    owner                 VARCHAR(255)  NOT NULL,               -- Repository Owner
    owner_url             TEXT,                                 -- Owner GitHub Profile URL
    repo_url              TEXT          NOT NULL,               -- Repository GitHub URL
    stars                 INT           NOT NULL,               -- Number of Stars
    forks                 INT           NOT NULL,               -- Number of Forks
    watchers              INT           NOT NULL,               -- Number of Watchers
    language              VARCHAR(50),                          -- Main Language of Repo
    description           TEXT,                                 -- Repository Description
    open_issues           INT                    DEFAULT 0,     -- Open Issues Count
    license_name          VARCHAR(255),                         -- License Type
    topics                TEXT[],                               -- Array of Topics/Tags
    default_branch        VARCHAR(50),                          -- Default Branch (main/master)
    commit_hash           VARCHAR(255),                         -- Last Commit Hash
    pushed_at             TIMESTAMP,                            -- Last Commit Push Timestamp
    repository_created_at TIMESTAMP,                            -- Repository Creation Date
    repository_updated_at TIMESTAMP,                            -- Last Update Timestamp
    created_at            TIMESTAMP              default now(),
    updated_at            TIMESTAMP

);


DROP TABLE IF EXISTS comment;
CREATE TABLE comment
(
    id                   BIGSERIAL PRIMARY KEY,
    uid                  VARCHAR(255) UNIQUE NOT NULL, -- Unique Comment Context ID
    repository_id        BIGINT              NOT NULL, -- Generated Repository ID
    repository_directory VARCHAR(255)        NOT NULL, -- Repository Directory
    commit_hash          VARCHAR(255),                 -- Commit Hash
    text                 TEXT,                         -- Comment Text
    start_line           INT                 NOT NULL, -- Start Line
    end_line             INT                 NOT NULL, -- End Line
    file                 VARCHAR(500),                 -- File Path and Name
    comment_hash         VARCHAR(255),                 -- Comment Hash
    is_td                BOOLEAN,                      -- Whether the comment is SATD
    is_random            BOOLEAN,                      -- Whether the comment is Randomly Picked for Manual Review
    td_type              VARCHAR(255),                 -- SATD Type
    note                 TEXT,                         -- Notes can be anything from dveloper's perspective
    language             VARCHAR(50),                  -- Main Language of the File
    code_before          TEXT,
    code_after           TEXT,
    created_at           TIMESTAMP default now(),
    updated_at           TIMESTAMP
);

ALTER TABLE comment
    ADD CONSTRAINT fk_comment_repository_id
        FOREIGN KEY (repository_id)
            REFERENCES repository (id);

ALTER TABLE comment
    ADD COLUMN code_before TEXT,
    ADD COLUMN code_after  TEXT;
