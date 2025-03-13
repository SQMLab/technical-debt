mvn clean package assembly:single

docker exec -i technical-debt-pgsql-1 psql -U satd -d postgres < /home/shahidul/dev/rnd/satd/dump/comment.sql


docker exec -i technical-debt-pgsql-1 psql -U satd -d postgres -At -c "SELECT 'UPDATE comment SET is_td = ' || COALESCE(is_td::TEXT, 'NULL') || ', note = ' || COALESCE(quote_literal(note), 'NULL') || ', td_type = ' || COALESCE(quote_literal(td_type), 'NULL') || ', is_random = ' || COALESCE(is_random::TEXT, 'NULL') || ', pred_td = ' || COALESCE(pred_td::TEXT, 'NULL') || ', updated_at = ' || COALESCE(quote_literal(updated_at::TEXT), 'NULL') || ' WHERE id = ' || id || ';' FROM comment WHERE is_random = TRUE or pred_td IS NOT NULL ORDER BY id;" > update-comment.sql