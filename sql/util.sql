-- Export Dataset
SELECT
       c.id,
       c.repository_id                                   AS repository,
       c.text                                            AS comment,
       CASE WHEN c.is_td = TRUE THEN 'yes' ELSE 'no' END AS satd,
       c.td_type                                         AS type,
       c.code_before,
       c.code_after,
       c.code_method,
       r.repo_url || '/blob/' || r.commit_hash || '/' ||
       c.file || '#L' || c.start_line          AS url

FROM comment c
JOIN repository r
     ON c.repository_id = r.id

WHERE c.is_random = TRUE
ORDER BY c.id;

-- Classified SATD Count
select td_type, count(id)
from comment
where td_type is not null
group by td_type;

-- Chinese Text Filter
select *
FROM comment
WHERE text ~* '[\u4e00-\u9fff]' and is_random = TRUE;

--  Matches non-Latin characters
SELECT *
FROM comment
WHERE NOT (text ~* '^[\x00-\x7F]*$')
AND is_random = TRUE;


-- Sample 10 Projects
SELECT
    r.name,
    r.stars,
    r.forks,
    r.watchers,
    COUNT(c.id) AS comments
FROM
    repository r
INNER JOIN
    comment c ON r.id = c.repository_id
WHERE
    r.id IN (6, 8, 11, 13, 15, 17, 19, 21, 26, 28, 32, 35, 37, 40, 47, 51, 53, 59, 60, 61, 63, 65, 66, 67, 69, 70, 73, 74, 77, 81, 83, 86, 87, 99, 104, 119, 127, 128, 129, 135, 144, 147, 164, 170, 173, 177, 182, 189, 203, 246, 272, 284, 287, 323, 348, 401, 483, 491, 546, 768)
GROUP BY
    r.id
LIMIT 10;

-- Top 10 project with high number of comments
SELECT
    r.name,
    r.stars,
    r.forks,
    r.watchers,
    COUNT(c.id) AS comments
FROM
    repository r
INNER JOIN
    comment c ON r.id = c.repository_id
GROUP BY
    r.id
order by COUNT(c.id) desc
LIMIT 10;

-- TOP 10 SATD project
SELECT
    r.name,
    COUNT(c.id) AS comments,
    COUNT(CASE WHEN c.is_random = true THEN 1 END) AS reviewed_comments,
    COUNT(CASE WHEN c.is_random = true AND c.is_td = true THEN 1 END) AS satd_comments,
    CONCAT(
        COUNT(CASE WHEN c.is_random = true AND c.is_td = true THEN 1 END),
        ' / ',
        COUNT(CASE WHEN c.is_random = true THEN 1 END)
    ) AS satd_comment_by_reviewed_comment,
    ROUND(
        100.0 * COUNT(CASE WHEN c.is_random = true AND c.is_td = true THEN 1 END)
        / NULLIF(COUNT(CASE WHEN c.is_random = true THEN 1 END), 0), 2
    ) AS satd_percentage
FROM
    repository r
INNER JOIN
    comment c ON r.id = c.repository_id
GROUP BY
    r.id
ORDER BY
    COUNT(CASE WHEN c.is_random = true THEN 1 END) DESC;
-- Repository
SELECT
    r.id,
    r.project_id,
    r.name,
    r.stars,
    r.forks,
    r.watchers,
    COUNT(c.id) AS comments,
    COUNT(c.id) FILTER (WHERE c.is_random = true) AS analyzed_comments,
    COUNT(c.id) FILTER (WHERE c.is_random = true AND c.is_td = true) AS satd_comments,
    ROUND(
        100.0 *
        (COUNT(c.id) FILTER (WHERE c.is_random = true))::numeric
        / NULLIF(COUNT(c.id), 0),
        2
    ) AS percent_analyzed_comments,
    ROUND(
        100.0 *
        (COUNT(c.id) FILTER (WHERE c.is_random = true AND c.is_td = true))::numeric
        / NULLIF(COUNT(c.id) FILTER (WHERE c.is_random = true), 0),
        2
    ) AS percent_satd_comments,
    r.repo_url,
    r.commit_hash,
    r.pushed_at,
    r.repository_created_at
FROM
    repository r
LEFT OUTER JOIN
    comment c
    ON r.id = c.repository_id
GROUP BY
    r.id
ORDER BY
    r.id;