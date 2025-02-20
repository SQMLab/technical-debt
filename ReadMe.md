mvn clean package assembly:single

docker exec -i satd-pgsql-1 psql -U satd -d postgres < /home/shahidul/dev/rnd/satd/dump/comment.sql


docker exec -i satd-pgsql-1 psql -U satd -d postgres -At -c "SELECT 'UPDATE comment SET is_td = ' || COALESCE(is_td::TEXT, 'NULL') || ', note = ' || COALESCE(quote_literal(note), 'NULL') || ', is_random = ' || COALESCE(is_random::TEXT, 'NULL') || ', updated_at = ' || COALESCE(quote_literal(updated_at::TEXT), 'NULL') || ' WHERE id = ' || id || ';' FROM comment WHERE is_random = TRUE ORDER BY id;" > update-comment.sql
