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
