SELECT id, text,
       CASE WHEN is_td = TRUE THEN 'yes' ELSE 'no' END AS label
FROM comment
WHERE is_td = TRUE
  AND repository_id != 69 order by id;
