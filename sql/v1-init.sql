DROP TABLE IF EXISTS repository;
CREATE TABLE repository
(
    id                    BIGSERIAL PRIMARY KEY,
    repository_id         BIGINT UNIQUE NOT NULL,               -- Unique GitHub Repository ID
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
