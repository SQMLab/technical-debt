-- Export Dataset
SELECT id,
       repository_id                                   as repository,
       text                                            as comment,
       CASE WHEN is_td = TRUE THEN 'yes' ELSE 'no' END AS satd,
       td_type                                         as type
from comment
where is_random = TRUE order by id;

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


-- 10 Well-Known Projects
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
    r.id IN (6, 8, 11, 13, 15, 17, 21, 28, 32, 40, 51, 53, 59, 60, 61, 63, 67, 69, 74, 81, 83, 86, 144, 173, 182)
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