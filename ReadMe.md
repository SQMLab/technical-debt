mvn clean package assembly:single

docker exec -i technical-debt-pgsql-1 psql -U satd -d postgres < /home/shahidul/dev/rnd/satd/dump/comment.sql


docker exec -i technical-debt-pgsql-1 psql -U satd -d postgres -At -c "SELECT 'UPDATE comment SET is_td = ' || COALESCE(is_td::TEXT, 'NULL') || ', note = ' || COALESCE(quote_literal(note), 'NULL') || ', td_type = ' || COALESCE(quote_literal(td_type), 'NULL') || ', is_random = ' || COALESCE(is_random::TEXT, 'NULL') || ', pred_td = ' || COALESCE(pred_td::TEXT, 'NULL') || ', updated_at = ' || COALESCE(quote_literal(updated_at::TEXT), 'NULL') || ' WHERE id = ' || id || ';' FROM comment WHERE is_random = TRUE or pred_td IS NOT NULL ORDER BY id;" > update-comment.sql


# testSATD

### Snakes in Paradise: A First Look at the Self-Admitted Technical Debt in Test code

## Introduction
Talk about software maintenance.. Say why, in addition to source code, test code is also important. Now say although SATD has been studied at source code, it's not done at test code.. now talk about your contribution and research questions.. 


RQ1: Can we detect test code SATD with the existing approaches?
RQ2? Can LLM detect SATD in test code?
RQ3? What are the types of test code SATD?
RQ4? Given an SATD, can LLM detect its type?
RQ5? Why do developers write SATD in test code? Manual analysis of all the SATDs under the new type only. 


## Related Work and Motivation:

Talk about the important papers that deal with test code and software quality and maintainability. 
Then talk about SATD?RQ1: Can we detect test code SATD with the existing approaches?
RQ2? Can LLM detect SATD in test code?
RQ3? What are the types of test code SATD?
RQ4? Given an SATD, can LLM detect its type?
RQ5? Why do developers write SATD in test code? Manual analysis of all the SATDs under the new
Now say we are interested about SATD in test code..

## Methodology
Project selection: we want to see SATD from diverse projects.. that's why top 1000 projects. 
How did you make sure test code only.. 
talk about Java parser and comment extraction.. 
Talk how you saved the positive and negative example..
Say that after some time we found most SATD comments are coming from one project only.. Therefore, we discarded that project. Don't delete data from that project.. Just add more data.. Make it at least 700 SATD comments.. 
Talk how three authors worked together on this.. 

## Results:
Discuss the approach and findings of each RQ. 

## Discussion:
What do the results mean, and what is the future work? 

##Threats to validity:

##Conclusion


